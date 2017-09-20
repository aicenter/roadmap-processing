import geojson
import networkx as nx
import codecs
from calculate_curvature import get_curvature
from geojson import LineString, Feature
import argparse
import sys

thresholds = [0, 0.01, 0.5, 1, 2]


def simplify(input_stream, output_stream, l_check, c_check):
    check_lanes = not l_check  # true means don't simplify edges with different num of lanes
    check_curvatures = c_check
    json_dict = load_geojson(input_stream)
    graph = load_graph(json_dict)
    simplify_graph(graph, check_lanes)
    prepare_to_saving_optimized(graph, json_dict)
    if check_curvatures:
        simplify_curvature(json_dict)
        json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    save_geojson(json_dict, output_stream)


def get_simplified_geojson(json_dict, l_check=False, c_check=False):
    check_lanes = not l_check  # true means don't simplify edges with different num of lanes
    check_curvatures = c_check
    graph = load_graph(json_dict)
    simplify_graph(graph, check_lanes)
    prepare_to_saving_optimized(graph, json_dict)
    if check_curvatures:
        simplify_curvature(json_dict)
        json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    return json_dict


def get_node(node):
    return (node[1], node[0])  # order latlon


def try_find(id, temp_dict):
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


def load_geojson(in_stream):
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
        res1 = get_curvature(first_edge)
        res2 = get_curvature(second_edge)
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
        is_loop = False  # finding oneway loop (from_id == to_id)
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
    temp_dict = dict()

    for edge in list_of_edges:
        id = edge[2]['id']
        temp_dict[id] = {}
        temp_dict[id]['node'] = edge[0]
        temp_dict[id]['neighbour'] = edge[1]
        temp_dict[id]['coords'] = edge[2]['others']

    counter = 0
    for item in json_dict['features']:
        data = try_find(item['properties']['id'], temp_dict)
        if data[0]:
            counter += 1
            item.clear()
        else:
            del item['geometry']['coordinates']
            item['geometry']['coordinates'] = data[1:]

    json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts


def save_geojson(json_dict, out_stream):
    geojson.dump(json_dict, out_stream)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
    parser.add_argument('-lanes', action='store_true', default=False, dest='lanes', help='simplify according lanes')
    parser.add_argument('-cur', action='store_true', default=False, dest='curs', help='simplify according curvatures\' thresholds')
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
    simplify(input_stream, output_stream, l_check=args.lanes, c_check=args.curs)
    input_stream.close()
    output_stream.close()
