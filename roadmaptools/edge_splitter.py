"""Creates new graph from the given graph so that the edges of the graph are not longer that the given edge_max_length. Includes all important data for AgentPolis"""
import argparse
import codecs

import math
from copy import deepcopy

import networkx as nx
from geojson import FeatureCollection, Feature, LineString

from roadmaptools.calculate_curvature import get_length
from roadmaptools.coords import get_distance_between_coords
from roadmaptools.utils import save_geojson, load_geojson, save_geojson_formatted
from roadmaptools.export_nodes_and_id_maker import export_nodes_in_geojson, get_node, get_geojson_with_unique_ids

__author__ = "Martin Schaefer"
__email__ = "martin@schaefer.cz"


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-edges', dest="output_edges", type=str, action='store', help='output edges file')
    parser.add_argument('-nodes', dest="output_nodes", type=str, action='store', help='output nodes file')
    return parser.parse_args()


# EXAMPLE OF USAGE
def add_edges(graph, edges):
    for (u, v, data) in edges:
        graph.add_edge(u, v, attr_dict=data)


def compute_coordinate(from_coord, to_coord, distance):

    overall_distance = get_distance_between_coords(from_coord, to_coord)
    percentage = distance / overall_distance
    if percentage < 0 or percentage > 1:
        print('ERROR')
        print(percentage)
        print(distance)
        print overall_distance
        exit()
    vect_x = to_coord[0] - from_coord[0]
    vect_y = to_coord[1] - from_coord[1]
    coord_x = from_coord[0] + percentage * vect_x
    coord_y = from_coord[1] + percentage * vect_y

    return [coord_x, coord_y]


def split_coordinates(coordinates, new_edge_length):
    length = 0
    end = 1
    next_part_dist = get_distance_between_coords(coordinates[0], coordinates[1])

    while end + 1 < len(coordinates) and length + next_part_dist < new_edge_length:
        length += next_part_dist
        end += 1
        next_part_dist = get_distance_between_coords(coordinates[end - 1], coordinates[end])

    remaining_length = new_edge_length - length
    if remaining_length > 0 and length + next_part_dist > new_edge_length:
        end_coordinate = compute_coordinate(coordinates[end - 1], coordinates[end], remaining_length)
        edge_coordinates = coordinates[0:end]
        edge_coordinates.append(end_coordinate)
        remaining_coordinates = coordinates[end:]
        remaining_coordinates.insert(0, end_coordinate)
    else:
        edge_coordinates = coordinates[0:end + 1]
        remaining_coordinates = coordinates[end:]

    if len(remaining_coordinates) <= 1:
        remaining_coordinates = []
    return edge_coordinates, remaining_coordinates, length + next_part_dist


def split_edge(edge, max_edge_length):
    (u, v, data) = edge
    overall_length = get_length(data['coordinates'])

    edges_count = math.floor(overall_length / max_edge_length)

    if edges_count > 1:
        new_edges = []
        ideal_edge_length = overall_length / edges_count
        coordinates = data['coordinates']
        remaining_coordinates = coordinates
        while remaining_coordinates:
            [new_coordinates, remaining_coordinates, edge_length] = split_coordinates(remaining_coordinates,
                                                                                      ideal_edge_length)

            new_data = deepcopy(data)
            new_data['coordinates'] = new_coordinates
            new_data['properties']['length'] = edge_length
            new_edges.append((get_node(new_coordinates[0]), get_node(new_coordinates[-1]), new_data))

    else:
        new_edges = [edge]
    return new_edges


def split_graph_edges(graph, max_edge_length=100.0):
    new_graph = nx.DiGraph()
    for edge in graph.edges(data=True):
        add_edges(new_graph, split_edge(edge, max_edge_length))

    return new_graph


def export_edges_in_geojson(graph):
    features = []
    id = 0
    for u, v, data in graph.edges(data=True):
        geometry = LineString((data["coordinates"]))
        properties = data["properties"]
        properties['id'] = id
        id += 1
        features.append(Feature(geometry=deepcopy(geometry), properties=deepcopy(properties)))

    return FeatureCollection(features)


def graph_to_jsons(graph):
    nodes = export_nodes_in_geojson(graph)
    edges = export_edges_in_geojson(graph)
    return [edges, nodes]


def load_graph(json_dict):
    g = nx.MultiDiGraph()
    for item in json_dict['features']:
        coord = item['geometry']['coordinates']
        coord_u = get_node(coord[0])
        coord_v = get_node(coord[-1])
        if coord_u != coord_v or len(coord) != 2:  # prune loops without any purpose, save loops like traffic roundabout
            data = {"coordinates": item['geometry']['coordinates'], "properties": item["properties"]}
            g.add_edge(coord_u, coord_v, attr_dict=data)
    return g


def process_graph(input_stream, output_stream_edges, output_stream_nodes, max_edge_length=100):
    graph = load_graph(load_geojson(input_stream))
    new_graph = split_graph_edges(graph, max_edge_length)

    [edges, nodes] = graph_to_jsons(new_graph)
    edges = get_geojson_with_unique_ids(edges)
    save_geojson_formatted(edges, output_stream_edges)
    save_geojson_formatted(nodes, output_stream_nodes)


if __name__ == '__main__':
    args = get_args()

    input_stream = codecs.open(args.input, encoding='utf8')
    output_stream_edges = codecs.open(args.output_edges, 'w')
    output_stream_nodes = codecs.open(args.output_nodes, 'w')

    process_graph(input_stream, output_stream_edges, output_stream_nodes,500)
    input_stream.close()
    output_stream_edges.close()
    output_stream_nodes.close()


def create_graph_with_short_edges(graph_geojson):
    new_graph = split_graph_edges(load_graph(graph_geojson))

    [edges, nodes] = graph_to_jsons(new_graph)
    return edges, nodes
