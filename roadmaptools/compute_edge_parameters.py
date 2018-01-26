import roadmaptools.inout
import geojson.feature
import networkx as nx

from typing import List, Dict
from roadmaptools.init import config

_computations = []


def compute_edge_parameters():
	geojson_file = roadmaptools.inout.load_geojson(config.simplified_file_with_speed_and_curvature)

	graph = roadmaptools.inout.load_graph(geojson_file)

	edge_map = _create_edge_map(graph)

	graph_multi_test(graph)

	_computations.append(compute_centrality)

	for computation in _computations:
		computation(graph, geojson_file, edge_map)

	roadmaptools.inout.save_geojson(geojson_file, config.completely_processed_geojson)


def compute_centrality(graph: nx.MultiDiGraph, data: geojson.feature.FeatureCollection, edge_map: Dict):
	for item in data['features']:
		edge = edge_map[item['properties']['id']]
		from_degree = graph.degree(edge[0])
		to_degree = graph.degree(edge[1])
		item['properties']["from_degree"] = from_degree
		item['properties']["to_degree"] = to_degree


def _create_edge_map(graph: nx.MultiDiGraph) -> Dict:
	edge_map = {}
	for edge in graph.edges():
		edge_map[graph[edge[0]][edge[1]][0]["id"]] = edge

	return edge_map


def graph_multi_test(graph: nx.MultiDiGraph):
	for edge in graph.edges():
		if len(graph[edge[0]][edge[1]]) > 1:
			a=1
