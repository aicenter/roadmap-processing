import geojson
import googlemaps
from datetime import datetime
import networkx as nx
import codecs
import os.path


class Data_from_gmapsAPI:  # GET ALL DATA FOR ALL TRAFFIC MODELS

    traffic_models = ["best_guess", "pessimistic", "optimistic"]
    temp_dict = dict()
    json_dict = dict()
    g = nx.MultiDiGraph()

    def __init__(self, pathname):
        self.pathname = pathname

    def find_edge(self, id, model):
        duration = self.temp_dict[id]['duration_' + model]
        distance = self.temp_dict[id]['distance_' + model]
        speed = self.temp_dict[id]['speed_' + model]
        return [duration, distance, speed]

    def get_node(self, node):
        return (node[1], node[0])  # order is latlon

    def load_file_and_graph(self):
        print "loading file..."
        with codecs.open(self.pathname, encoding='utf8') as f:
            self.json_dict = geojson.load(f)
        f.close()

        if os.path.exists("temp_data.gpickle"):
            self.g = nx.read_gpickle("temp_data.gpickle")

    def get_gmaps_data(self):
        print "getting data from googlemaps..."
        self.check_abnormal_speeds()

        for n, nbrsdict in self.g.adjacency_iter():
            for nbr, keydict in nbrsdict.items():
                for key, d in keydict.items():
                    self.temp_dict[d['id']] = {}
                    for model in self.traffic_models:
                        try:
                            self.temp_dict[d['id']]['duration_' + model] = d['duration_' + model]
                            self.temp_dict[d['id']]['distance_' + model] = d['distance_' + model]
                            self.temp_dict[d['id']]['speed_' + model] = d['speed_' + model]
                        except:
                            print "data missing"

        for item in self.json_dict['features']:
            if item != {}:
                for model in self.traffic_models:
                    try:
                        res = self.find_edge(item['properties']['id'], model)  # return duration, distance, speed
                        item['properties']['duration_' + model] = res[0]
                        item['properties']['distance_' + model] = res[1]
                        item['properties']['speed_' + model] = res[2]
                    except:
                        print "data missing"

    def check_abnormal_speeds(self):
        for n, nbrsdict in self.g.adjacency_iter():
            for nbr, keydict in nbrsdict.items():
                for key, d in keydict.items():
                    for model in self.traffic_models:
                        try:
                            if d['speed_' + model] == 0:  # check zero speeds
                                list_of_neighbours = [self.g.in_edges(n, data=True), self.g.out_edges(nbr, data=True)]
                                number_of_nonzero_results = 0
                                summary_of_speeds = 0
                                for edges in list_of_neighbours:
                                    for i in range(0, len(edges)):
                                        if (n, nbr) != (edges[i][0], edges[i][1]) and (n, nbr) != (
                                        edges[i][1], edges[i][0]):
                                            act_speed = edges[i][2]['speed_' + model]
                                            if act_speed != 0:
                                                number_of_nonzero_results += 1
                                                summary_of_speeds += act_speed
                                d['speed_' + model] = summary_of_speeds / number_of_nonzero_results
                        except:
                            print "data missing"

        for n, nbrsdict in self.g.adjacency_iter():
            for nbr, keydict in nbrsdict.items():
                for key, d in keydict.items():
                    for model in self.traffic_models:
                        try:
                            avg_in_sum = 0
                            avg_in_counter = 0
                            avg_out_sum = 0
                            avg_out_counter = 0
                            for edge in self.g.in_edges(n, data=True):
                                if (n, nbr) != (edge[0], edge[1]) and (n, nbr) != (edge[1], edge[0]):
                                    avg_in_sum += edge[2]['speed_' + model]
                                    avg_in_counter += 1
                            for edge in self.g.out_edges(nbr, data=True):
                                if (n, nbr) != (edge[0], edge[1]) and (n, nbr) != (edge[1], edge[0]):
                                    avg_out_sum += edge[2]['speed_' + model]
                                    avg_out_counter += 1
                            if avg_in_counter != 0 or avg_out_counter != 0:  # PAK TOTO SMAZ!!
                                if avg_in_counter == 0:
                                    avg_out = avg_out_sum / avg_out_counter
                                    if self.decide_low_or_high_speed(d['speed_' + model], avg_out) != 0:
                                        d['speed_' + model] = avg_out
                                elif avg_out_counter == 0:
                                    avg_in = avg_in_sum / avg_in_counter
                                    if self.decide_low_or_high_speed(d['speed_' + model], avg_in) != 0:
                                        d['speed_' + model] = avg_in
                                else:
                                    avg_in = avg_in_sum / avg_in_counter
                                    avg_out = avg_out_sum / avg_out_counter
                                    if self.decide_low_or_high_speed(d['speed_' + model],
                                                                     avg_in) == 1 and self.decide_low_or_high_speed(
                                            d['speed_' + model], avg_out) == 1:
                                        d['speed_' + model] = (avg_out + avg_in) / 2
                                    elif self.decide_low_or_high_speed(d['speed_' + model],
                                                                       avg_in) == -1 and self.decide_low_or_high_speed(
                                            d['speed_' + model], avg_out) == -1:
                                        d['speed_' + model] = (avg_out + avg_in) / 2
                        except:
                            print "data missing"

    def decide_low_or_high_speed(self, speed, avg_speed):
        ret = 0

        if speed * 2 < avg_speed:  # check abnormaly low speed
            ret = -1
        elif speed / 2 > avg_speed:  # check abnormaly high speed
            ret = 1

        return ret

    def save_file_to_geojson(self):
        print "saving file..."
        with open("result-temporary.geojson", 'w') as outfile:
            geojson.dump(self.json_dict, outfile, indent=4, sort_keys=True)
        outfile.close()


# EXAMPLE
test = Data_from_gmapsAPI("graph_with_simplified_edges.geojson")
test.load_file_and_graph()
test.get_gmaps_data()
test.save_file_to_geojson()
