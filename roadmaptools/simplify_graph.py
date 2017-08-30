from __future__ import print_function
import geojson
import networkx as nx
import codecs
from calculate_curvature import calculate_curvature
from geojson import LineString, Feature
import argparse
import sys
import copy
from export_nodes_and_id_maker import export_points_to_geojson

temp_dict = dict()
temp_features = list()
temp_edges = list()
thresholds = [0, 0.01, 0.5, 1, 2]


def simplify(input_stream, output_stream, l_check, c_check, sim):
    check_lanes = not l_check  # true means don't simplify edges with different num of lanes
    check_curvatures = c_check
    json_dict = load_file(input_stream)
    graph = load_graph(json_dict)
    if sim:
        subgraph = get_largest_component(graph)
        graph = traverse_and_create_graph(graph, subgraph)
    simplify_graph(graph, check_lanes)
    if sim:
        detect_parallel_edges(graph)
        id_iter = find_max_id(json_dict) + 1  # new id iterator
        for edge in temp_edges:
            add_new_edges(json_dict, edge, id_iter)
            id_iter += 2
    prepare_to_saving_optimized(graph, json_dict)
    if sim:
        json_dict['features'].extend(temp_features)
        export_points_to_geojson(json_dict)
    if check_curvatures:
        simplify_curvature(json_dict)
        json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    save_file_to_geojson(json_dict, output_stream)


def export_nodes(json_dict):
    temp_graph = nx.MultiDiGraph()
    for item in json_dict['features']:
        coords = item['geometry']['coordinates']
        u = get_node_for_exporting(coords[0])
        v = get_node_for_exporting(coords[-1])
        temp_graph.add_edge(u, v)

    export_points_to_geojson(temp_graph)


def get_node_for_exporting(node):
    return (node[0], node[1])  # order lonlat


def get_largest_component(graph):
    biggest_subgraph = graph

    if not nx.is_strongly_connected(graph):
        maximum_number_of_nodes = -1
        for subgraph in nx.strongly_connected_components(graph):
            if len(subgraph) > maximum_number_of_nodes:
                maximum_number_of_nodes = len(subgraph)
                biggest_subgraph = subgraph
    return biggest_subgraph


def traverse_and_create_graph(g, subgraph):
    temp_g = nx.MultiDiGraph()
    for n, nbrsdict in g.adjacency_iter():
        if n in subgraph:
            for nbr, keydict in nbrsdict.items():
                if nbr in subgraph:
                    for key, d in keydict.items():
                        temp_g.add_edge(n, nbr, id=d['id'], others=d['others'], lanes=d['lanes'])
    return temp_g


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


def find_max_id(json_dict):
    max_id = -1
    for item in json_dict['features']:
        if item['properties']['id'] > max_id:
            max_id = item['properties']['id']
    return max_id


def add_new_edges(json_dict, edge, new_id):  # don't delete item it isn't necessary, because it's made automatically before saving
    for item in json_dict['features']:
        if edge[0]['id'] == item['properties']['id']:
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
                break


def get_node(node):
    return (node[1], node[0])  # order latlon


def get_node_reversed(node):
    return [node[1], node[0]]  # latlon


def try_find(id):
    if id in temp_dict:
        n1 = temp_dict[id]['node'][1]
        n2 = temp_dict[id]['node'][0]
        nbr1 = temp_dict[id]['neighbour'][1]
        nbr2 = temp_dict[id]['neighbour'][0]
        coords = filter(None, temp_dict[id]['coords'])
        ret = [False, [n1, n2]]
        for node in coords:
            ret.append(node)
        ret.append([nbr1, nbr2])
        return ret
    else:
        return [True]


def load_file(in_stream):
    json_dict = geojson.load(in_stream)
    return json_dict


def load_graph(json_dict):
    g = nx.MultiDiGraph()
    for item in json_dict['features']:
        coord = item['geometry']['coordinates']
        coord_u = get_node(coord[0])
        coord_v = get_node(coord[-1])
        if coord_u != coord_v or len(coord) != 2:  # prune loops without any purpose, save loops like traffic roundabout
            lanes = item['properties']['lanes']
            g.add_edge(coord_u, coord_v, id=item['properties']['id'], others=[[]], lanes=lanes)
    return g


def simplify_graph(g, check_lanes):
    for n, _ in g.adjacency_iter():
        if g.out_degree(n) == 1 and g.in_degree(n) == 1:  # oneways
            simplify_oneways(n, g, check_lanes)

    for n, _ in g.adjacency_iter():
        if g.out_degree(n) == 2 and g.in_degree(n) == 2:  # both directions in highway
            simplify_twoways(n, g, check_lanes)


def get_threshold(curvature):
    counter = 0
    for i in range(0, len(thresholds) - 1):
        if thresholds[i] < curvature and curvature < thresholds[i + 1]:
            return counter
        counter += 1
    return counter  # bigger then last interval


def cut_edges_off(item, id_iterator, json_dict):
    coords = item['geometry']['coordinates']
    first_edge = coords[0:3]
    end = False
    last_node = 0
    for i in range(3, len(coords), 2):
        if len(coords[i - 1:len(coords)]) < 5:
            second_edge = coords[i - 1:len(coords)]
            end = True
        else:
            second_edge = coords[i - 1:i + 2]
        res1 = calculate_curvature(first_edge)
        res2 = calculate_curvature(second_edge)
        u = get_threshold(res1[0])
        v = get_threshold(res2[0])
        if u != v:
            line_string = LineString(coordinates=coords[last_node:i])
            last_node = i - 1
            id_iterator += 1
            feature = Feature(geometry=line_string, id=id_iterator, properties=item['properties'])
            json_dict['features'].append(feature)
        if end == True:
            break
        else:
            first_edge = second_edge

    line_string = LineString(coordinates=coords[last_node:len(coords)])
    feature = Feature(geometry=line_string, id=id_iterator + 1, properties=item['properties'])
    return [feature, id_iterator + 1]


def simplify_curvature(json_dict):
    length = len(json_dict['features'])
    id_iterator = length + 1
    for i in range(0, length):
        if len(json_dict['features'][i]['geometry']['coordinates']) > 4:
            res = cut_edges_off(json_dict['features'][i], id_iterator, json_dict)
            feature = res[0]
            id_iterator = res[1] + 1
            json_dict['features'].append(feature)
            json_dict['features'][i].clear()


def simplify_oneways(n, g, check_lanes):
    edge_u = g.out_edges(n, data=True)[0][:2]
    temp = reversed(edge_u)
    edge_u = tuple(temp)
    edge_v = g.in_edges(n, data=True)[0][:2]
    new_id = g.out_edges(n, data=True)[0][2]['id']
    coords = filter(None, g.in_edges(n, data=True)[0][2]['others'] + [[n[1], n[0]]] + g.out_edges(n, data=True)[0][2]['others'])
    lanes_u = g.out_edges(n, data=True)[0][2]['lanes']
    lanes_v = g.in_edges(n, data=True)[0][2]['lanes']
    if edge_u != edge_v:
        # remove edges and node
        if lanes_u == lanes_v or lanes_u is None or lanes_v is None or check_lanes:  # merge only edges with same number of lanes
            g.add_edge(edge_v[0], edge_u[0], id=new_id, others=coords, lanes=lanes_u)
            g.remove_edge(edge_u[1], edge_u[0])
            g.remove_edge(edge_v[0], edge_v[1])
            g.remove_node(n)
    elif edge_u == edge_v and hash_list_of_lists_and_compare(g.in_edges(n, data=True)[0][2]['others'], g.out_edges(n, data=True)[0][2]['others']):
        if lanes_u == lanes_v or lanes_u is None or lanes_v is None or check_lanes:  # merge only edges with same number of lanes
            g.add_edge(edge_v[0], edge_u[0], id=new_id, others=coords, lanes=lanes_u)
            g.remove_edge(edge_u[1], edge_u[0])
            g.remove_edge(edge_v[0], edge_v[1])
            g.remove_node(n)


def hash_list_of_lists_and_compare(list1, list2):
    temp_hash1 = [tuple(i) for i in list1]
    temp_hash2 = [tuple(i) for i in list2]
    return set(temp_hash1) != set(temp_hash2)


def simplify_twoways(n, g, check_lanes):
    edge_u1 = g.out_edges(n, data=True)[0][:2]
    edge_u2 = g.out_edges(n, data=True)[1][:2]
    temp1 = reversed(edge_u1)
    edge_u1 = tuple(temp1)
    temp2 = reversed(edge_u2)
    edge_u2 = tuple(temp2)
    new_id_out = g.out_edges(n, data=True)[0][2]['id']
    new_id_in = g.in_edges(n, data=True)[0][2]['id']
    coords_out = filter(None, g.in_edges(n, data=True)[1][2]['others'] + [[n[1], n[0]]] + g.out_edges(n, data=True)[0][2]['others'])
    coords_in = list(reversed(coords_out))
    edge_v1 = g.in_edges(n, data=True)[0][:2]
    edge_v2 = g.in_edges(n, data=True)[1][:2]
    edges_u = (edge_u1, edge_u2)
    edges_v = (edge_v1, edge_v2)
    lanes_u1 = g.out_edges(n, data=True)[0][2]['lanes']
    lanes_u2 = g.out_edges(n, data=True)[1][2]['lanes']
    lanes_v1 = g.in_edges(n, data=True)[0][2]['lanes']
    lanes_v2 = g.in_edges(n, data=True)[1][2]['lanes']
    if edges_u == edges_v:
        # remove edges and node
        is_deleted = [False, False]
        is_loop = False
        for i in edges_u:
            if check_oneway_loop(i):
                is_loop = True
        for i in edges_v:
            if check_oneway_loop(i):
                is_loop = True
        if is_loop:
            return
        if lanes_u1 == lanes_v2 or lanes_u1 is None or lanes_v2 is None or check_lanes:  # merge only edges with same number of lanes
            g.remove_edge(edge_u1[1], edge_u1[0])
            g.remove_edge(edge_u2[0], edge_u2[1])
            g.add_edge(edge_v2[0], edge_v1[0], id=new_id_out, others=coords_out, lanes=lanes_u1)
            is_deleted[0] = True
        if lanes_u2 == lanes_v1 or lanes_u2 == None or lanes_v1 == None or check_lanes:  # merge only edges with same number of lanes
            if edge_u1[1] != edge_u1[0] or edge_u2[0] != edge_u2[1]:  # check  loops
                g.remove_edge(edge_u1[0], edge_u1[1])
                g.remove_edge(edge_u2[1], edge_u2[0])
                g.add_edge(edge_v1[0], edge_v2[0], id=new_id_in, others=coords_in, lanes=lanes_v1)
                is_deleted[1] = True

        if is_deleted[0] == True and is_deleted[1] == True or check_lanes:
            g.remove_node(n)


def check_oneway_loop(edge):
    return edge[0] == edge[1]


def prepare_to_saving_optimized(g, json_dict):
    list_of_edges = list(g.edges_iter(data=True))

    for edge in list_of_edges:
        id = edge[2]['id']
        temp_dict[id] = {}
        temp_dict[id]['node'] = edge[0]
        temp_dict[id]['neighbour'] = edge[1]
        temp_dict[id]['coords'] = edge[2]['others']

    counter = 0
    for item in json_dict['features']:
        data = try_find(item['properties']['id'])
        if data[0]:
            counter += 1
            item.clear()
        else:
            del item['geometry']['coordinates']
            item['geometry']['coordinates'] = data[1:]

    json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts


def save_file_to_geojson(json_dict, out_stream):
    geojson.dump(json_dict, out_stream)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
    parser.add_argument('-lanes', action='store_true', default=False, dest='lanes', help='simplify according lanes')
    parser.add_argument('-cur', action='store_true', default=False, dest='curs', help='simplify according curvatures\' thresholds')
    parser.add_argument('-sim', action='store_true', default=False, dest='sim', help='simplify according lanes')
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

    # l_check set True whether you don't want to simplify edges with different number of lanes
    # c_check set True whether you don't want to simplify edges with different curvature
    simplify(input_stream, output_stream, l_check=args.lanes, c_check=args.curs, sim=args.sim)
    input_stream.close()
    output_stream.close()
