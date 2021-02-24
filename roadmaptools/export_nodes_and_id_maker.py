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
import codecs
from geojson import Point, Feature, FeatureCollection
import networkx as nx
import sys
import argparse
import roadmaptools.graph


def create_unique_ids(input_stream, output_stream, formated):
    json_dict = load_geojson(input_stream)
    # points = export_points_to_geojson(json_dict)
    # save_geojson(points, output_stream, formated)
    get_ids(json_dict)
    save_geojson(json_dict, output_stream, formated)


def get_geojson_with_unique_ids(json_dict):
    get_ids(json_dict)
    return json_dict


def get_node(node):
    return (node[0], node[1])  # order lonlat


def load_geojson(in_stream):
    json_dict = geojson.load(in_stream)
    return json_dict


def load_graph(json_dict):
    g = nx.DiGraph()
    for item in json_dict['features']:
        coord = item['geometry']['coordinates']
        coord_u = get_node(coord[0])
        coord_v = get_node(coord[-1])
        g.add_edge(coord_u, coord_v, id=item['properties']['id'])
    return g


def get_node_collection(json_dict):
    g = load_graph(json_dict)
    list_of_features = []
    index = 0
    for n in g.nodes():
        node_id = roadmaptools.graph.get_node_id(n)
        point = Point(n)
        feature = Feature(geometry=point, properties={'node_id': node_id, 'index': index})
        list_of_features.append(feature)
        index += 1

    json_dict_with_points = FeatureCollection(features=list_of_features)

    return json_dict_with_points


def get_ids(json_dict):
    for item in json_dict['features']:
        # item['properties']['length'] = item['properties']['distance_best_guess']
        # item['properties']['speed'] = item['properties']['speed_best_guess']
        # del item['properties']['distance_best_guess']
        # if 'distance_optimistic' in item['properties']:
        #     del item['properties']['distance_optimistic']
        # if 'distance_pessimistic' in item['properties']:
        #     del item['properties']['distance_pessimistic']

        from_node = item['geometry']['coordinates'][0]
        to_node = item['geometry']['coordinates'][-1]
        from_node_id = roadmaptools.graph.get_node_id(from_node)
        to_node_id = roadmaptools.graph.get_node_id(to_node)
        item['properties']['from_id'] = from_node_id
        item['properties']['to_id'] = to_node_id


def save_geojson(json_dict, out_stream, is_formated=False):
    if is_formated == False:
        geojson.dump(json_dict, out_stream)
    else:
        geojson.dump(json_dict, out_stream, indent=4, sort_keys=True)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
    parser.add_argument('-formated', action='store_true', default=False, dest='formated', help='format output file')
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

    create_unique_ids(input_stream, output_stream, args.formated)
    input_stream.close()
    output_stream.close()
