import numpy as np
import roadmaptools.inout

from typing import List
from geojson import FeatureCollection


def create_adj_matrix(nodes_filepath: str, edges_filepath: str, out_filepath: str):
	nodes = roadmaptools.inout.load_geojson(nodes_filepath)
	edges = roadmaptools.inout.load_geojson(edges_filepath)
	dm = get_adj_matrix(nodes, edges)
	roadmaptools.inout.save_csv(dm, out_filepath)


def get_adj_matrix(nodes: FeatureCollection, edges: FeatureCollection) -> np.ndarray:
	nodes = nodes['features']
	size = len(nodes)
	adj = np.full((size, size), np.nan)
	node_dict = {node['properties']['node_id']: node for node in nodes}
	for edge in edges['features']:
		from_node = node_dict[edge['properties']['from_id']]
		to_node = node_dict[edge['properties']['to_id']]
		distance = edge['properties']['length']
		adj[from_node['properties']['index'], to_node['properties']['index']] = distance

	return adj

