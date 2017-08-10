from __future__ import division
import geojson
import googlemaps
from datetime import datetime
import networkx as nx
import codecs
import os.path
import math
from KEY_PROVIDER import key
import logging
import sys

class Data_from_gmapsAPI:  # GET ALL DATA FOR ALL TRAFFIC MODELS

    traffic_models = ["best_guess", "pessimistic", "optimistic"]
    temp_dict = dict()
    json_dict = dict()
    g = nx.MultiDiGraph()

    def __init__(self, pathname):
        self.logger = logging.getLogger('gmaps_data_errors')
        hdlr = logging.FileHandler('data/data_from_gmaps.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.WARNING)  # warnings and worse
        self.gmaps = googlemaps.Client(key=key)
        self.pathname = pathname

    def find_edge(self, id, model):
        duration = self.temp_dict[id]['duration_' + model]
        distance = self.temp_dict[id]['distance_' + model]
        speed = self.temp_dict[id]['speed_' + model]
        return [duration, distance, speed]

    def google_maps_request(self, vertex_u, vertex_v, model, coords):  # now works with all traffic models
        try:
            time = datetime(2017, 11, 14, 7, 0, 0)  # 7 hours after midnight 14.11.2017
            result = self.gmaps.distance_matrix(vertex_u, vertex_v, mode="driving", language="en-GB", units="metric", departure_time=time, traffic_model=model)
            print result

            try:
                duration = result['rows'][0]['elements'][0]['duration_in_traffic']['value']
            except:
                duration = result['rows'][0]['elements'][0]['duration']['value']

            distance = result['rows'][0]['elements'][0]['distance']['value']

            if duration==0:
                duration = 1

            speed = float(distance / duration) * 3.6

            print '{} {}'.format(speed, 'km/h')
            if self.is_distance_correct(coords, distance):  # is data from gmaps correct
                return [duration, distance, speed]
            else:
                distance_new = self.get_distance_single_edge(coords)
                res = self.get_new_duration_and_speed(coords, distance_new, model)
                self.logger.warning('Duration %f -> %f', duration, res[0])
                self.logger.warning('Distance %f -> %f', distance, res[1])
                self.logger.warning('Speed %f -> %f', speed, res[2])
                return res

        except (googlemaps.exceptions.Timeout, googlemaps.exceptions.TransportError, googlemaps.exceptions.ApiError):  # save temporary progress
            print "gmaps_ERROR!"
            nx.write_gpickle(self.g, "data/temp_data.gpickle")
            exit()

    def set_check_gmaps(self, value):
        self.check = value

    def get_node(self, node):
        return (node[1], node[0])  # order is latlon

    def get_distance_between_two_coords(self, point1, point2):  # return in meters
        R = 6371000
        lat1 = math.radians(point1[0])
        lat2 = math.radians(point2[0])
        lat = math.radians(point2[0] - point1[0])
        lon = math.radians(point2[1] - point1[1])

        a = math.sin(lat / 2) * math.sin(lat / 2) + math.cos(lat1) * math.cos(lat2) * math.sin(lon / 2) * math.sin(lon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    def get_distance_single_edge(self, coords):
        distance = 0
        for i in range(0, len(coords) - 1):
            u = self.get_node(coords[i])
            v = self.get_node(coords[i + 1])
            distance += self.get_distance_between_two_coords(u, v)
        return distance

    def get_new_duration_and_speed(self, coords, distance, model):  # return duration,distance,speed
        new_distance = distance
        last = self.get_node(coords[-1])
        if len(coords) == 2:
            return [-1, distance, 0]  # must be approximated by neighbours
        else:
            u = self.get_node(coords[0])
            v = self.get_node(coords[1])
            new_distance -= self.get_distance_between_two_coords(u, v)
            result = self.google_maps_request(v, last, model, coords[1:])
            error = self.get_error(result[1], new_distance)
            if error <= 0.1:
                try:
                    duration = distance / (result[2]/3.6)
                except:
                    duration = -1
                return [duration, distance, result[2]]  # must be approximated by neighbours

    def get_error(self, estimated_distance, precised_distance):
        return abs(estimated_distance - precised_distance) / precised_distance

    def is_distance_correct(self, coords, estimated_distance):
        if self.check == False:
            return True
        precised_distance = self.get_distance_single_edge(coords)
        error = self.get_error(estimated_distance, precised_distance)
        if error > 0.2:
            return False
        else:
            return True

    def load_file_and_graph(self):
        print "loading file..."
        with codecs.open(self.pathname, encoding='utf8') as f:
            self.json_dict = geojson.load(f)
        f.close()

        if os.path.exists("data/temp_data.gpickle"):
            self.g = nx.read_gpickle("data/temp_data.gpickle")
        else:
            for item in self.json_dict['features']:
                coord = item['geometry']['coordinates']
                coord_u = self.get_node(coord[0])
                coord_v = self.get_node(coord[-1])
                self.g.add_edge(coord_u, coord_v, id=item['properties']['id'], coords=coord)

    def get_gmaps_data(self):
        print "getting data from googlemaps..."
        for n, nbrsdict in self.g.adjacency_iter():
            for nbr, keydict in nbrsdict.items():
                for key, d in keydict.items():
                    for model in self.traffic_models:
                        val = 'speed_' + model
                        if val not in d:
                            res = self.google_maps_request(n, nbr, model, d['coords'])  # return duration, distance, speed
                            d['duration_' + model] = res[0]
                            d['distance_' + model] = res[1]
                            d['speed_' + model] = res[2]

        nx.write_gpickle(self.g, "data/temp_data.gpickle")  # save for sure

        if self.check == True:
            self.check_abnormal_speeds()

        for n, nbrsdict in self.g.adjacency_iter():
            for nbr, keydict in nbrsdict.items():
                for key, d in keydict.items():
                    self.temp_dict[d['id']] = {}
                    for model in self.traffic_models:
                        self.temp_dict[d['id']]['duration_' + model] = d['duration_' + model]
                        self.temp_dict[d['id']]['distance_' + model] = d['distance_' + model]
                        self.temp_dict[d['id']]['speed_' + model] = d['speed_' + model]

        for item in self.json_dict['features']:
            for model in self.traffic_models:
                res = self.find_edge(item['properties']['id'], model)  # return duration, distance, speed
                item['properties']['duration_' + model] = res[0]
                item['properties']['distance_' + model] = res[1]
                item['properties']['speed_' + model] = res[2]

    def write_to_log(self, speed, new_speed, duration, new_duration, id):
        self.logger.warning('Speed %f -> %f id: %d', speed, new_speed, id)
        self.logger.warning('Duration %f -> %f id: %d', duration, new_duration, id)

    def check_abnormal_speeds(self):
        self.logger.warning('--------------------------------------------')
        repeat = True
        while repeat:
            repeat = False
            for n, nbrsdict in self.g.adjacency_iter():
                for nbr, keydict in nbrsdict.items():
                    for key, d in keydict.items():
                        for model in self.traffic_models:
                            if d['speed_' + model] == 0:  # check zero speeds
                                list_of_neighbours = [self.g.in_edges(n, data=True), self.g.out_edges(nbr, data=True)]
                                number_of_nonzero_results = 0
                                summary_of_speeds = 0
                                for edges in list_of_neighbours:
                                    for i in range(0, len(edges)):
                                        if (n, nbr) != (edges[i][0], edges[i][1]) and (n, nbr) != (edges[i][1], edges[i][0]):
                                            act_speed = edges[i][2]['speed_' + model]
                                            if act_speed != 0:
                                                number_of_nonzero_results += 1
                                                summary_of_speeds += act_speed

                                if number_of_nonzero_results == 0:
                                    if list_of_neighbours[0] == [] and list_of_neighbours[1] == []:  # it shouldn't happen
                                        d['speed_' + model] = -1
                                        d['duration_' + model] = -1
                                    else:
                                        repeat = True
                                else:
                                    d['speed_' + model] = summary_of_speeds / number_of_nonzero_results
                                    d['duration_' + model] = d['distance_' + model] / (d['speed_' + model] / 3.6)
                                    self.write_to_log(0, d['speed_' + model], -1, d['duration_' + model], d['id'])

        for n, nbrsdict in self.g.adjacency_iter():
            for nbr, keydict in nbrsdict.items():
                for key, d in keydict.items():
                    for model in self.traffic_models:  # check too high or too low speed
                        avg_in_sum = 0
                        avg_in_counter = 0
                        avg_out_sum = 0
                        avg_out_counter = 0
                        min_range_in = sys.maxint
                        min_range_out = sys.maxint
                        value_speed_out = 0
                        value_speed_in = 0
                        value_speed = d['speed_' + model]
                        for edge in self.g.in_edges(n, data=True):
                            if (n, nbr) != (edge[0], edge[1]) and (n, nbr) != (edge[1], edge[0]):
                                temp = abs(value_speed-edge[2]['speed_' + model])
                                if temp < min_range_in: #change edge_speed only according the closest speed
                                    min_range_in = temp
                                    value_speed_in = edge[2]['speed_' + model]
                                avg_in_sum += edge[2]['speed_' + model]
                                avg_in_counter += 1
                        for edge in self.g.out_edges(nbr, data=True):
                            if (n, nbr) != (edge[0], edge[1]) and (n, nbr) != (edge[1], edge[0]):
                                temp = abs(value_speed-edge[2]['speed_' + model])
                                if temp < min_range_out: #change edge_speed only according the closest speed
                                    min_range_out = temp
                                    value_speed_out = edge[2]['speed_' + model]
                                avg_out_sum += edge[2]['speed_' + model]
                                avg_out_counter += 1

                        if avg_in_counter != 0 or avg_out_counter != 0:  # due to unreachable edges, it shouldn't happen in graph of Prague
                            if avg_in_counter == 0:
                                avg_out = avg_out_sum / avg_out_counter
                                if self.decide_low_or_high_speed(d['speed_' + model], value_speed_out) != 0:
                                    self.write_to_log(d['speed_' + model], avg_out, d['duration_' + model], d['distance_' + model] / (avg_out / 3.6), d['id'])
                                    d['speed_' + model] = avg_out
                                    d['duration_' + model] = d['distance_' + model] / (d['speed_' + model] / 3.6)
                            elif avg_out_counter == 0:
                                avg_in = avg_in_sum / avg_in_counter
                                if self.decide_low_or_high_speed(d['speed_' + model], value_speed_in) != 0:
                                    self.write_to_log(d['speed_' + model], avg_in, d['duration_' + model], d['distance_' + model] / (avg_in / 3.6), d['id'])
                                    d['speed_' + model] = avg_in
                                    d['duration_' + model] = d['distance_' + model] / (d['speed_' + model] / 3.6)
                            else:
                                avg_in = avg_in_sum / avg_in_counter
                                avg_out = avg_out_sum / avg_out_counter
                                if self.decide_low_or_high_speed(d['speed_' + model], value_speed_in) == 1 and self.decide_low_or_high_speed(d['speed_' + model], value_speed_out) == 1:
                                    self.write_to_log(d['speed_' + model], (avg_out + avg_in) / 2, d['duration_' + model], d['distance_' + model] / (((avg_out + avg_in) / 2) / 3.6), d['id'])
                                    d['speed_' + model] = (avg_out + avg_in) / 2
                                    d['duration_' + model] = d['distance_' + model] / (d['speed_' + model] / 3.6)
                                elif self.decide_low_or_high_speed(d['speed_' + model], value_speed_in) == -1 and self.decide_low_or_high_speed(d['speed_' + model], value_speed_out) == -1:
                                    self.write_to_log(d['speed_' + model], (avg_out + avg_in) / 2, d['duration_' + model], d['distance_' + model] / (((avg_out + avg_in) / 2) / 3.6), d['id'])
                                    d['speed_' + model] = (avg_out + avg_in) / 2
                                    d['duration_' + model] = d['distance_' + model] / (d['speed_' + model] / 3.6)

    def decide_low_or_high_speed(self, speed, avg_speed):
        ret = 0
        if speed * 2 < avg_speed:  # check abnormaly low speed
            ret = -1
        elif speed / 2 > avg_speed:  # check abnormaly high speed
            ret = 1
        return ret

    def save_file_to_geojson(self):
        print "saving file..."
        with open("data/gmaps-out.geojson", 'w') as outfile:
            geojson.dump(self.json_dict, outfile)
        outfile.close()

# EXAMPLE
if __name__ == '__main__':
    test = Data_from_gmapsAPI("graph_with_simplified_edges.geojson")
    test.check(True) #check whether gmaps data is correct
    test.load_file_and_graph()
    test.get_gmaps_data()
    test.save_file_to_geojson()
