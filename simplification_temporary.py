from __future__ import division
from geojson import LineString, Feature
import networkx as nx
import codecs
from simplify_graph import load_file, prepare_to_saving_optimized, save_file_to_geojson, simplify_graph
import copy
from postprocess_geojson import export_points_to_geojson


##udelat komponenty a detekce vice hran mezi 2 nody

def traverse_and_create_graph(g, subgraph):
    temp_g = nx.MultiDiGraph()
    for n, nbrsdict in g.adjacency_iter():
        if n in subgraph:
            for nbr, keydict in nbrsdict.items():
                if nbr in subgraph:
                    for key, d in keydict.items():
                        temp_g.add_edge(n, nbr, id=d['id'], others=d['others'], lanes=d['lanes'])
    return temp_g


def get_nodeID(node_id):  # return String
    lon = int(node_id[0] * 10 ** 6)
    lat = int(node_id[1] * 10 ** 6)
    return str(lat) + str(lon)


def find_max_id(json_dict):
    max_id = -1
    for item in json_dict['features']:
        # print item['properties']['id']
        if item['properties']['id'] > max_id:
            max_id = item['properties']['id']
    return max_id


def get_node_for_exporting(node):
    return (node[0], node[1])  # order lonlat


def get_node(node):
    return (node[1], node[0])  # order latlon


def detect_parallel_edges(g):
    set_of_edges = set()
    for n, nbrsdict in g.adjacency_iter():
        for nbr, keydict in nbrsdict.items():
            for key, d in keydict.items():
                if key != 0:
                    if (n, nbr) in set_of_edges:
                        temp_edges.append((g[n][nbr][key], get_node_reversed(n), get_node_reversed(nbr), True))
                    else:
                        set_of_edges.add((nbr, n)) #add the second direction to set!!
                        temp_edges.append((g[n][nbr][key], get_node_reversed(n), get_node_reversed(nbr), False))
                    g.remove_edge(n, nbr, key)
    print len(set_of_edges)


def get_node_reversed(node):
    return [node[1], node[0]]


def add_new_edges(json_dict, edge, new_id):  # don't delete item it isn't necessary, because it's made automatically before saving
    for item in json_dict['features']:
        if edge[0]['id'] == item['properties']['id']:
            if len(edge[0]['others']) > 0:
                if edge[3]==True:
                    print edge[0]['others']
                    edge[0]['others'].insert(0,edge[1])
                    line_string1 = LineString(coordinates=(edge[0]['others']))
                    line_string2 = LineString(coordinates=(edge[0]['others'][-1],edge[2]))
                    print line_string1
                    print line_string2
                else:
                    line_string1 = LineString(coordinates=(edge[1], edge[0]['others'][0]))
                    edge[0]['others'].append(edge[2])
                    line_string2 = LineString(coordinates=edge[0]['others'])

                feature1 = Feature(geometry=line_string1, properties=copy.deepcopy(item['properties']))
                feature1['properties']['id'] = new_id
                feature2 = Feature(geometry=line_string2, properties=copy.deepcopy(item['properties']))
                feature2['properties']['id'] = new_id + 1
                temp_features.append(feature1)
                temp_features.append(feature2)
                break
            else:
                # must be added new point
                # y = a*x + b
                x = (edge[1][0] + edge[2][0]) / 2
                y = (edge[1][1] + edge[2][1]) / 2
                edge[0]['others'] = [[x, y]]
                if edge[3]==True:
                    print edge[0]['others']
                    edge[0]['others'].insert(0,edge[1])
                    line_string1 = LineString(coordinates=(edge[0]['others']))
                    line_string2 = LineString(coordinates=(edge[0]['others'][-1],edge[2]))
                    print line_string1
                    print line_string2
                else:
                    line_string1 = LineString(coordinates=(edge[1], edge[0]['others'][0]))
                    edge[0]['others'].append(edge[2])
                    line_string2 = LineString(coordinates=edge[0]['others'])
                # line_string1 = LineString(coordinates=(edge[1], edge[0]['others'][0]))
                # edge[0]['others'].append(edge[2])
                # line_string2 = LineString(coordinates=edge[0]['others'])

                feature1 = Feature(geometry=line_string1, properties=copy.deepcopy(item['properties']))
                feature1['properties']['id'] = new_id
                feature2 = Feature(geometry=line_string2, properties=copy.deepcopy(item['properties']))
                feature2['properties']['id'] = new_id + 1
                temp_features.append(feature1)
                temp_features.append(feature2)
                break


def load_graph(json_dict):
    g = nx.MultiDiGraph()
    for item in json_dict['features']:
        coord = item['geometry']['coordinates']
        coord_u = get_node(coord[0])
        coord_v = get_node(coord[-1])
        if coord_u != coord_v or len(coord) != 2:  # prune loops without any purpose, save loops like traffic roundabout
            lanes = item['properties']['lanes']
            data = item['geometry']['coordinates'][1:-1]
            if len(data) == 0:
                data = [[]]
            g.add_edge(coord_u, coord_v, id=item['properties']['id'], others=data, lanes=lanes)
    return g


temp_edges = list()
f = codecs.open("data/output-result.geojson", 'r')
json_dict = load_file(f)
f.close()

graph = load_graph(json_dict)
biggest_subgraph = set()

if not nx.is_strongly_connected(graph):
    maximum_number_of_nodes = -1
    for subgraph in nx.strongly_connected_components(graph):
        if len(subgraph) > maximum_number_of_nodes:
            maximum_number_of_nodes = len(subgraph)
            biggest_subgraph = subgraph

            # print maximum_number_of_nodes,biggest_subgraph

new_graph = traverse_and_create_graph(graph, biggest_subgraph)

simplify_graph(new_graph, False)

detect_parallel_edges(new_graph)

temp_features = list()

id_iter = find_max_id(json_dict) + 1  # new id iterator
# print id_iter

# print(temp_edges)
for edge in temp_edges:
    add_new_edges(json_dict, edge, id_iter)
    id_iter += 2

# json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
prepare_to_saving_optimized(new_graph, json_dict)

# f = open("data/output-deleted.geojson", 'w')
# my_dict ={}
# my_dict['features']=temp_features
# my_dict['type']='FeatureCollection'
# save_file_to_geojson(my_dict, f)
# f.close()


json_dict['features'].extend(temp_features)

temp_graph = nx.MultiDiGraph()
for item in json_dict['features']:
    coords = item['geometry']['coordinates']
    u = get_node_for_exporting(coords[0])
    v = get_node_for_exporting(coords[-1])
    temp_graph.add_edge(u, v)

export_points_to_geojson(temp_graph)

f = open("data/output-test.geojson", 'w')
save_file_to_geojson(json_dict, f)
f.close()
