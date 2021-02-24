#
# Copyright (c) 2021 Czech Technical University in Prague.
#
# This file is part of Roadmaptools 
# (see https://github.com/aicenter/roadmap-processing).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import geojson
import networkx as nx
import codecs
from roadmaptools.calculate_curvature import get_curvature
from geojson import LineString, Feature, FeatureCollection
import argparse
import sys
import time
import roadmaptools.inout
import roadmaptools.road_structures

from tqdm import tqdm
from roadmaptools.init import config
from roadmaptools.printer import print_info

thresholds = [0, 0.01, 0.5, 1, 2]


def simplify_geojson(input_file=config.sanitized_geojson_file, output_file=config.simplified_file):
    print_info('Simplifying geoJSON')
    start_time = time.time()

    # l_check set True whether you don't want to simplify edges with different number of lanes
    # c_check set True whether you don't want to simplify edges with different curvature
    geojson_file = roadmaptools.inout.load_geojson(input_file)

    print_info("Simplification process started")
    geojson_out = get_simplified_geojson(geojson_file, l_check=False, c_check=False)

    print_info('Simplification completed. (%.2f secs)' % (time.time() - start_time))

    roadmaptools.inout.save_geojson(geojson_out, output_file)


def simplify(input_filepath, output_filepath, l_check, c_check):
    check_lanes = not l_check  # true means don't simplify edges with different num of lanes
    check_curvatures = c_check
    json_dict = roadmaptools.inout.load_geojson(input_filepath)
    graph = _load_graph(json_dict)
    _simplify_graph(graph, check_lanes)
    _prepare_to_saving_optimized(graph, json_dict)
    if check_curvatures:
        _simplify_curvature(json_dict)
        json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    roadmaptools.inout.save_geojson(json_dict, output_filepath)


def _is_multidigraph(g: nx.MultiDiGraph) -> bool:
    for node, nbrdict in g.adjacency():
        for nbr, attributes in nbrdict.items():
            if len(attributes) > 1:
                return True
    return False


def _get_max_id_in_graph(g: nx.MultiDiGraph) -> int:
    max_id = -1
    for n, nbrdict in g.adjacency():
        for nbr, attrs in nbrdict.items():
            for i in range(len(attrs)):
                if max_id < attrs[i]['id']:
                    max_id = attrs[i]['id']
    return max_id


def create_digraph(graph: nx.MultiDiGraph) -> nx.DiGraph:
    if not _is_multidigraph(graph):
        return nx.DiGraph(graph)

    # id_counter = _get_max_id_in_graph(graph) + 1
    new_graph = nx.DiGraph()
    for n, nbrdict in graph.adjacency():
        for nbr, attributes in nbrdict.items():
            if not type(attributes) is dict:
                id_counter = 0
                for i in range(len(attributes)):
                    if attributes[i]['others'] == [[]]:
                        new_graph.add_edge(n, nbr, id='{}_{}'.format(attributes[i]['id'], id_counter), lanes=attributes[i]['lanes'],
                                           others=attributes[i]['others'])
                        id_counter += 1
                    else:
                        temp_nbr = get_node(attributes[i]['others'][0])
                        new_graph.add_edge(n, temp_nbr, id='{}_{}'.format(attributes[i]['id'], id_counter),
                                           lanes=attributes[i]['lanes'], others=[[]])
                        id_counter += 1
                        new_graph.add_edge(temp_nbr, nbr, id='{}_{}'.format(attributes[i]['id'], id_counter),
                                           lanes=attributes[i]['lanes'], others=attributes[i]['others'][1:])
                        id_counter += 1

            else:
                new_graph.add_edge(n, nbr, id=attributes['id'], lanes=attributes['lanes'], others=attributes[
                    'others'])
    return new_graph


def get_simplified_geojson(json_dict: FeatureCollection, l_check=False, c_check=False):
    check_lanes = not l_check  # true means don't simplify edges with different num of lanes
    check_curvatures = c_check
    graph = _load_graph(json_dict)
    _simplify_graph(graph, check_lanes)
    graph = create_digraph(graph)
    _prepare_to_saving_optimized(graph, json_dict)
    if check_curvatures:
        _simplify_curvature(json_dict)
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


def _load_graph(json_dict: dict) -> nx.MultiDiGraph:
    g = nx.DiGraph()
    for item in tqdm(json_dict['features'], desc="creating road graph"):
        coord = item['geometry']['coordinates']
        coord_u = get_node(coord[0])
        coord_v = get_node(coord[-1])
        if coord_u != coord_v or len(coord) != 2:  # prune loops without any purpose, save loops like traffic roundabout
            lanes = item['properties']['lanes']
            g.add_edge(coord_u, coord_v, id=item['properties']['id'], others=[[]], lanes=lanes)
    return g


def _simplify_graph(g: nx.MultiDiGraph, check_lanes):
    for n, _ in tqdm(list(g.adjacency()), desc="simplifying oneways"):
        if g.out_degree(n) == 1 and g.in_degree(n) == 1:  # oneways
            simplify_oneways(n, g, check_lanes)

    for n, _ in tqdm(list(g.adjacency()), desc="simplifying bidirectional"):
        if g.out_degree(n) == 2 and g.in_degree(n) == 2:  # both directions in highway
            simplify_twoways(n, g, check_lanes)


def get_threshold(curvature):
    counter = 0
    for i in range(0, len(thresholds) - 1):
        if thresholds[i] < curvature and curvature < thresholds[i + 1]:
            return counter
        counter += 1
    return counter  # bigger then last interval


def _cut_edges_off(item, id_iterator, json_dict):
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


def _simplify_curvature(json_dict):
    length = len(json_dict['features'])
    id_iterator = length + 1
    for i in range(0, length):
        if len(json_dict['features'][i]['geometry']['coordinates']) > 4:
            res = _cut_edges_off(json_dict['features'][i], id_iterator, json_dict)
            feature = res[0]
            id_iterator = res[1] + 1
            json_dict['features'].append(feature)
            json_dict['features'][i].clear()


def simplify_oneways(n, g, check_lanes):
    edge_u = list(g.out_edges(n, data=True))[0][:2]
    temp = reversed(edge_u)
    edge_u = tuple(temp)
    edge_v = list(g.in_edges(n, data=True))[0][:2]
    new_id = list(g.out_edges(n, data=True))[0][2]['id']
    coords = list(filter(None, list(g.in_edges(n, data=True))[0][2]['others'] + [[n[1], n[0]]]
                         + list(g.out_edges(n, data=True))[0][2]['others']))
    lanes_u = list(g.out_edges(n, data=True))[0][2]['lanes']
    lanes_v = list(g.in_edges(n, data=True))[0][2]['lanes']
    if edge_u != edge_v:
        # remove edges and node
        if lanes_u == lanes_v or lanes_u is None or lanes_v is None or check_lanes:  # merge only edges with same number of lanes
            g.add_edge(edge_v[0], edge_u[0], id=new_id, others=coords, lanes=lanes_u)
            g.remove_edge(edge_u[1], edge_u[0])
            g.remove_edge(edge_v[0], edge_v[1])
            g.remove_node(n)
    elif edge_u == edge_v and hash_list_of_lists_and_compare(list(g.in_edges(n, data=True))[0][2]['others'],
                                                             list(g.out_edges(n, data=True))[0][2]['others']):
        if lanes_u == lanes_v or lanes_u is None or lanes_v is None or check_lanes:  # merge only edges with same number of lanes
            g.add_edge(edge_v[0], edge_u[0], id=new_id, others=coords, lanes=lanes_u)
            g.remove_edge(edge_u[1], edge_u[0])
            g.remove_edge(edge_v[0], edge_v[1])
            g.remove_node(n)


def hash_list_of_lists_and_compare(list1, list2):
    temp_hash1 = [tuple(i) for i in list1]
    temp_hash2 = [tuple(i) for i in list2]
    return set(temp_hash1) != set(temp_hash2)


def simplify_twoways(n, g: nx.MultiDiGraph, check_lanes: bool):
    edge_u1 = list(g.out_edges(n, data=True))[0][:2]
    edge_u2 = list(g.out_edges(n, data=True))[1][:2]
    temp1 = reversed(edge_u1)
    edge_u1 = tuple(temp1)
    temp2 = reversed(edge_u2)
    edge_u2 = tuple(temp2)
    new_id_out = list(g.out_edges(n, data=True))[0][2]['id']
    new_id_in = list(g.in_edges(n, data=True))[0][2]['id']
    coords_out = list(filter(None, list(g.in_edges(n, data=True))[1][2]['others'] + [[n[1], n[0]]]
                             + list(g.out_edges(n, data=True))[0][2]['others']))
    coords_in = list(reversed(coords_out))
    edge_v1 = list(g.in_edges(n, data=True))[0][:2]
    edge_v2 = list(g.in_edges(n, data=True))[1][:2]
    edges_u = (edge_u1, edge_u2)
    edges_v = (edge_v1, edge_v2)
    lanes_u1 = list(g.out_edges(n, data=True))[0][2]['lanes']
    lanes_u2 = list(g.out_edges(n, data=True))[1][2]['lanes']
    lanes_v1 = list(g.in_edges(n, data=True))[0][2]['lanes']
    lanes_v2 = list(g.in_edges(n, data=True))[1][2]['lanes']
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
        if lanes_u2 == lanes_v1 or lanes_u2 is None or lanes_v1 is None or check_lanes:  # merge only edges with same number of lanes
            if edge_u1[1] != edge_u1[0] or edge_u2[0] != edge_u2[1]:  # check  loops
                g.remove_edge(edge_u1[0], edge_u1[1])
                g.remove_edge(edge_u2[1], edge_u2[0])
                g.add_edge(edge_v1[0], edge_v2[0], id=new_id_in, others=coords_in, lanes=lanes_v1)
                is_deleted[1] = True

        if is_deleted[0] and is_deleted[1] or check_lanes:
            g.remove_node(n)


def check_oneway_loop(edge):
    return edge[0] == edge[1]


def _prepare_to_saving_optimized(g, json_dict):
    list_of_edges = list(g.edges(data=True))
    temp_dict = dict()

    for edge in list_of_edges:
        id = edge[2]['id']
        temp_dict[id] = {}
        temp_dict[id]['node'] = edge[0]
        temp_dict[id]['neighbour'] = edge[1]
        temp_dict[id]['coords'] = edge[2]['others']

    json_ids = dict()
    for item in json_dict['features']:
        if item['properties']['id'] not in json_ids:
            json_ids[item['properties']['id']] = [item]

    for item in json_dict['features']:
        data = try_find(item['properties']['id'], temp_dict)
        if data[0]:
            # item.clear()
            json_ids[item['properties']['id']].append(True)
        else:
            del item['geometry']['coordinates']
            item['geometry']['coordinates'] = data[1:]

    features = []

    for key, value in temp_dict.items():
        if isinstance(key,str) and "_" in key:
            data = try_find(key, temp_dict)
            item = json_ids[int(key.split("_")[0])][0]
            linestring = LineString(coordinates=data[1:])
            # del item['geometry']['coordinates']
            # item['geometry']['coordinates'] = data[1:]
            # from_coords =
            # item['properties']['id'] = counter
            feature = Feature(geometry=linestring, id=item['id'], properties=item['properties'])
            features.append(feature)

    for key, linestring in json_ids.items():
        if len(linestring)>1:
            linestring[0].clear()

    json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    json_dict['features'].extend(features)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
    parser.add_argument('-lanes', action='store_true', default=False, dest='lanes', help='simplify according lanes')
    parser.add_argument('-cur', action='store_true', default=False, dest='curs',
                        help='simplify according curvatures\' thresholds')
    return parser.parse_args()


# EXAMPLE OF USAGE
if __name__ == '__main__':
    args = get_args()
    # input_stream = sys.stdin
    # output_stream = sys.stdout
    #
    # if args.input is not None:
    # 	input_stream = codecs.open(args.input, encoding='utf8')
    # if args.output is not None:
    # 	output_stream = codecs.open(args.output, 'w')

    # l_check set True whether you don't want to simplify edges with different number of lanes
    # c_check set True whether you don't want to simplify edges with different curvature
    simplify(args.input, args.output, l_check=args.lanes, c_check=args.curs)
