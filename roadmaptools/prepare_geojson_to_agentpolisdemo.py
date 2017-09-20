from __future__ import division
from geojson import LineString, Feature
import networkx as nx
import codecs
from simplify_graph import load_geojson, prepare_to_saving_optimized, save_geojson
import copy
from export_nodes_and_id_maker import export_points_to_geojson, get_ids
import sys
import argparse

temp_edges = list()
temp_features = list()


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
                        set_of_edges.add((nbr, n))  # add the second direction to set!!
                        temp_edges.append((g[n][nbr][key], get_node_reversed(n), get_node_reversed(nbr), False))
                    g.remove_edge(n, nbr, key)


def get_node_reversed(node):
    return [node[1], node[0]]


def add_new_edges(json_dict, edge, new_id):  # don't delete item it isn't necessary, because it's made automatically before saving
    for item in json_dict['features']:
        if item != {} and edge[0]['id'] == item['properties']['id']:
            if len(edge[0]['others']) > 0:
                if edge[3] == True:
                    edge[0]['others'].insert(0, edge[1])
                    line_string1 = LineString(coordinates=(edge[0]['others']))
                    line_string2 = LineString(coordinates=(edge[0]['others'][-1], edge[2]))
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
                item.clear()
                break
            else:
                # must be added new point
                # y = a*x + b
                x = (edge[1][0] + edge[2][0]) / 2
                y = (edge[1][1] + edge[2][1]) / 2
                edge[0]['others'] = [[x, y]]
                if edge[3] == True:
                    edge[0]['others'].insert(0, edge[1])
                    line_string1 = LineString(coordinates=(edge[0]['others']))
                    line_string2 = LineString(coordinates=(edge[0]['others'][-1], edge[2]))
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
                item.clear()
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
                data = []
            g.add_edge(coord_u, coord_v, id=item['properties']['id'], others=data, lanes=lanes)
    return g


def get_biggest_component(graph):
    biggest_subgraph = graph

    if not nx.is_strongly_connected(graph):
        maximum_number_of_nodes = -1
        for subgraph in nx.strongly_connected_components(graph):
            if len(subgraph) > maximum_number_of_nodes:
                maximum_number_of_nodes = len(subgraph)
                biggest_subgraph = subgraph
    return biggest_subgraph


def create_DiGraph(g):
    temp_gr = nx.DiGraph()
    for n, nbrsdict in g.adjacency_iter():
        for nbr, keydict in nbrsdict.items():
            for key, d in keydict.items():
                temp_gr.add_edge(n, nbr, lanes=d['lanes'], id=d['id'], others=d['others'])
    return temp_gr


def prepare_graph_to_agentpolisdemo(input_stream, output_stream):
    json_dict = load_geojson(input_stream)
    graph = load_graph(json_dict)
    biggest_subgraph = get_biggest_component(graph)
    new_graph = traverse_and_create_graph(graph, biggest_subgraph)

    detect_parallel_edges(new_graph)
    id_iter = find_max_id(json_dict) + 1  # new id iterator
    for edge in temp_edges:
        add_new_edges(json_dict, edge, id_iter)
        id_iter += 2
    json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    prepare_to_saving_optimized(new_graph, json_dict)
    json_dict['features'].extend(temp_features)
    get_ids(json_dict)
    nodes = export_points_to_geojson(json_dict)
    # print len(json_dict['features'])
    # output_stream = open("/home/martin/MOBILITY/GITHUB/smaz/agentpolis-demo/python_scripts/data/nodes.geojson",'w')
    # save_geojson(nodes, output_stream)
    # output_stream.close()
    # for item in json_dict['features']:
    #     item['properties']['length']=1
    #     item['properties']['speed']=1
    # output_stream = open("/home/martin/MOBILITY/GITHUB/smaz/agentpolis-demo/python_scripts/data/edges.geojson",'w')
    save_geojson(json_dict, output_stream)
    # output_stream.close()


def get_nodes_and_edges_for_agentpolisdemo(json_dict):
    graph = load_graph(json_dict)
    biggest_subgraph = get_biggest_component(graph)
    new_graph = traverse_and_create_graph(graph, biggest_subgraph)

    detect_parallel_edges(new_graph)
    id_iter = find_max_id(json_dict) + 1  # new id iterator
    for edge in temp_edges:
        add_new_edges(json_dict, edge, id_iter)
        id_iter += 2
    json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    prepare_to_saving_optimized(new_graph, json_dict)
    json_dict['features'].extend(temp_features)
    get_ids(json_dict)
    nodes = export_points_to_geojson(json_dict)
    for item in json_dict['features']:
        if item['properties']['id']==3544:
            print("grr")
    return [json_dict, nodes]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
    return parser.parse_args()


# EXAMPLE OF USAGE
if __name__ == '__main__':
    args = get_args()
    input_stream = sys.stdin
    output_stream = sys.stdout

    if args.input is not None:
        input_stream = codecs.open(args.input, encoding='utf8')
    if args.output is not None:
        output_stream = codecs.open(args.output, 'w')

    prepare_graph_to_agentpolisdemo(input_stream, output_stream)
    input_stream.close()
    output_stream.close()
