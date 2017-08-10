import geojson
import networkx as nx
import codecs
from curvature import Calculation_curvature
import numpy as np
from geojson import LineString,Feature

class Simplifying_graph():

    g = nx.MultiDiGraph()
    temp_dict = dict()
    curve = Calculation_curvature("not important at all")
    thresholds = [0,0.01,0.5,1,2]

    def __init__(self,filename):
        self.filename = filename

    def get_node(self,node):
        return (node[1],node[0]) #order latlon

    def set_simplify_lanes(self,check): #true means dont simplify edges with different num of lanes
        self.check_lanes = not check

    def set_simplify_curvature(self,check):
        self.check_curvature = check

    def set_thresholds(self,thresholds):
        self.thresholds = thresholds

    def try_find(self,id):
        if id in self.temp_dict:
            n1 = self.temp_dict[id]['node'][1]
            n2 = self.temp_dict[id]['node'][0]
            nbr1 = self.temp_dict[id]['neighbour'][1]
            nbr2 = self.temp_dict[id]['neighbour'][0]
            coords = filter(None,self.temp_dict[id]['coords'])
            ret = [False,[n1,n2]]
            for node in coords:
                ret.append(node)
            ret.append([nbr1,nbr2])
            return ret
        else:
            return [True]


    def load_file_and_graph(self):
        print "loading file..."
        with codecs.open(self.filename,encoding='utf8') as f:
                self.json_dict = geojson.load(f)
        f.close()

        self.id_iterator = len(self.json_dict['features'])

        for item in self.json_dict['features']:
            coord = item['geometry']['coordinates']
            coord_u = self.get_node(coord[0])
            coord_v = self.get_node(coord[-1])
            if coord_u != coord_v or len(coord) != 2:  # prune loops without any purpose, save loops like traffic roundabout
                lanes = item['properties']['lanes']
                self.g.add_edge(coord_u, coord_v, id=item['properties']['id'], others=[[]], lanes=lanes)

    def simplify_graph(self):
        print "processing...\nbefore simplifying.."
        print "number of nodes: ",self.g.number_of_nodes()
        print "number of edges: ",self.g.number_of_edges()

        for n,_ in self.g.adjacency_iter():
            if self.g.out_degree(n)==1 and self.g.in_degree(n)==1: #oneways
                self.simplify_oneways(n)
            elif self.g.out_degree(n)==2 and self.g.in_degree(n)==2:#both directions in highway
                self.simplify_twoways(n)

        print "after simplifying.."
        print "number of nodes: ", self.g.number_of_nodes()
        print "number of edges: ", self.g.number_of_edges()

    def get_threshold(self,curvature):
        counter = 0
        for i in range(0,len(self.thresholds)-1):
            if self.thresholds[i] < curvature and curvature < self.thresholds[i+1]:
                return counter
            counter += 1
        return counter #bigger then last interval

    def cut_edges_off(self,item):
        coords = item['geometry']['coordinates']
        first_edge = coords[0:3]
        #print coords
        #print first_edge
        end = False
        last_node = 0
        for i in range(3,len(coords),2):
            if len(coords[i-1:len(coords)]) < 5:
                second_edge = coords[i-1:len(coords)]
                end = True
            else:
                second_edge = coords[i-1:i+2]
            #print second_edge
            res1 = self.curve.calculate_curvature(first_edge)
            res2 = self.curve.calculate_curvature(second_edge)
            #print res1,res2
            u = self.get_threshold(res1[0])
            v = self.get_threshold(res2[0])
            #print u,v
            if u!=v:
                line_string = LineString(coordinates=coords[last_node:i])
                #print line_string
                last_node = i-1
                #print coords[last_node]
                self.id_iterator += 1
                feature = Feature(geometry=line_string,id=self.id_iterator,properties=item['properties'])
                self.json_dict['features'].append(feature)
            if end==True:
                break
            else:
                first_edge = second_edge

        line_string = LineString(coordinates=coords[last_node:len(coords)])
        #print line_string
        #print coords[last_node]
        self.id_iterator += 1
        feature = Feature(geometry=line_string, id=self.id_iterator, properties=item['properties'])
        self.json_dict['features'].append(feature)



    def simplify_curvature(self):
        print len(self.json_dict['features'])
        length = len(self.json_dict['features'])
        for i in range(0,length):
            if len(self.json_dict['features'][i]['geometry']['coordinates']) > 4:
                self.cut_edges_off(self.json_dict['features'][i])
                self.json_dict['features'][i].clear()

        print len(self.json_dict['features'])


    def simplify_oneways(self,n):
        edge_u = self.g.out_edges(n, data=True)[0][:2]
        temp = reversed(edge_u)
        edge_u = tuple(temp)
        edge_v = self.g.in_edges(n, data=True)[0][:2]
        new_id = self.g.out_edges(n, data=True)[0][2]['id']
        coords = filter(None, self.g.in_edges(n, data=True)[0][2]['others'] + [[n[1], n[0]]] + self.g.out_edges(n, data=True)[0][2]['others'])
        lanes_u = self.g.out_edges(n, data=True)[0][2]['lanes']
        lanes_v = self.g.in_edges(n, data=True)[0][2]['lanes']
        if edge_u != edge_v:
            # remove edges and node
            if lanes_u == lanes_v or lanes_u == None or lanes_v == None or self.check_lanes:  # merge only edges with same number of lanes
                self.g.add_edge(edge_v[0], edge_u[0], id=new_id, others=coords, lanes=lanes_u)
                self.g.remove_edge(edge_u[1], edge_u[0])
                self.g.remove_edge(edge_v[0], edge_v[1])
                self.g.remove_node(n)

    def simplify_twoways(self,n):
        edge_u1 = self.g.out_edges(n, data=True)[0][:2]
        edge_u2 = self.g.out_edges(n, data=True)[1][:2]
        temp1 = reversed(edge_u1)
        edge_u1 = tuple(temp1)
        temp2 = reversed(edge_u2)
        edge_u2 = tuple(temp2)
        new_id_out = self.g.out_edges(n, data=True)[0][2]['id']
        new_id_in = self.g.in_edges(n, data=True)[0][2]['id']
        coords_out = filter(None, self.g.in_edges(n, data=True)[1][2]['others'] + [[n[1], n[0]]] + self.g.out_edges(n, data=True)[0][2]['others'])
        coords_in = list(reversed(coords_out))
        edge_v1 = self.g.in_edges(n, data=True)[0][:2]
        edge_v2 = self.g.in_edges(n, data=True)[1][:2]
        edges_u = (edge_u1, edge_u2)
        edges_v = (edge_v1, edge_v2)
        lanes_u1 = self.g.out_edges(n, data=True)[0][2]['lanes']
        lanes_u2 = self.g.out_edges(n, data=True)[1][2]['lanes']
        lanes_v1 = self.g.in_edges(n, data=True)[0][2]['lanes']
        lanes_v2 = self.g.in_edges(n, data=True)[1][2]['lanes']
        if edges_u == edges_v:
            # remove edges and node
            is_deleted = [False, False]
            if lanes_u1 == lanes_v2 or lanes_u1 == None or lanes_v2 == None or self.check_lanes:  # merge only edges with same number of lanes
                self.g.remove_edge(edge_u1[1], edge_u1[0])
                self.g.remove_edge(edge_u2[0], edge_u2[1])
                self.g.add_edge(edge_v2[0], edge_v1[0], id=new_id_out, others=coords_out, lanes=lanes_u1)
                is_deleted[0] = True
            if lanes_u2 == lanes_v1 or lanes_u2 == None or lanes_v1 == None or self.check_lanes:  # merge only edges with same number of lanes
                if edge_u1[1] != edge_u1[0] or edge_u2[0] != edge_u2[1]:  # check self loops
                    self.g.remove_edge(edge_u1[0], edge_u1[1])
                    self.g.remove_edge(edge_u2[1], edge_u2[0])
                    self.g.add_edge(edge_v1[0], edge_v2[0], id=new_id_in, others=coords_in, lanes=lanes_v1)
                    is_deleted[1] = True

            if is_deleted[0] == True and is_deleted[1] == True or self.check_lanes:
                self.g.remove_node(n)

    def prepare_to_saving_optimized(self):
        list_of_edges = list(self.g.edges_iter(data=True))

        for edge in list_of_edges:
            id = edge[2]['id']
            self.temp_dict[id]= {}
            self.temp_dict[id]['node']=edge[0]
            self.temp_dict[id]['neighbour']=edge[1]
            self.temp_dict[id]['coords']=edge[2]['others']

        counter = 0
        for item in self.json_dict['features']:
            data = self.try_find(item['properties']['id'])
            if data[0]:
                counter += 1
                item.clear()
            else:
                del item['geometry']['coordinates']
                item['geometry']['coordinates'] = data[1:]

        print "number of deleted edges: ",counter

    def save_file_to_geojson(self):
        print "saving file..."
        self.json_dict['features'] = [i for i in self.json_dict["features"] if i]  # remove empty dicts
        if self.check_curvature == True:
            self.simplify_curvature()
        self.json_dict['features'] = [i for i in self.json_dict["features"] if i] #remove empty dicts
        with open("data/graph_with_simplified_edges.geojson", 'w') as outfile:
            geojson.dump(self.json_dict, outfile)
        outfile.close()

#EXAMPLE OF USAGE
if __name__ == '__main__':
    test = Simplifying_graph("data/pruned_file.geojson")
    test.load_file_and_graph()
    test.set_simplify_lanes(False) #set True whether you don't want to simplify edges with different number of lanes
    test.set_simplify_curvature(False) #set True whether you don't want to simplify edges with different curvature
    test.simplify_graph()
    test.prepare_to_saving_optimized()
    test.save_file_to_geojson()

