import networkx as nx
import roadmaptools.inout

from networkx import DiGraph
from geojson.feature import FeatureCollection
from tqdm import tqdm
from roadmaptools.init import config
from roadmaptools.printer import print_info


def get_biggest_component(graph: DiGraph) -> set:
	biggest_subgraph = graph

	if not nx.is_strongly_connected(graph):
		maximum_number_of_nodes = -1
		for subgraph in nx.strongly_connected_components(graph):
			if len(subgraph) > maximum_number_of_nodes:
				maximum_number_of_nodes = len(subgraph)
				biggest_subgraph = subgraph

	id_dict = nx.get_edge_attributes(graph, "id")

	print_info("Creating edge id set")
	edge_ids = set()
	for coordinates, id in id_dict.items():
		if coordinates[0] in biggest_subgraph and coordinates[1] in biggest_subgraph:
			edge_ids.add(id)

	return edge_ids


def filter_geojson_features_by_graph(geojson_data: FeatureCollection, edge_ids: set):

	print_info("Filtering geojson by edge id set")
	new_features = []
	for item in tqdm(geojson_data['features'], desc="processing features"):
		if item['properties']['id'] in edge_ids:
			new_features.append(item)

	geojson_data["features"] = new_features


# def _detect_parallel_edges(graph):
# 	set_of_edges = set()
# 	for n, nbrsdict in list(graph.adjacency()):
# 		for nbr, keydict in nbrsdict.items():
# 			for key, d in keydict.items():
# 				if key != 0:
# 					if (n, nbr) in set_of_edges:
# 						temp_edges.append((graph[n][nbr][key], get_node_reversed(n), get_node_reversed(nbr), True))
# 					else:
# 						set_of_edges.add((nbr, n))  # add the second direction to set!!
# 						temp_edges.append((graph[n][nbr][key], get_node_reversed(n), get_node_reversed(nbr), False))
# 					graph.remove_edge(n, nbr, key)


def sanitize(input_filepath: str=config.cleaned_geojson_file, output_filepath: str=config.sanitized_geojson_file):
	"""
	return only the biggest component from map
	:return:
	"""
	geojson_data = roadmaptools.inout.load_geojson(input_filepath)

	graph = roadmaptools.inout.load_graph(geojson_data)
	biggest_component_set = get_biggest_component(graph)
	# _detect_parallel_edges(biggest_component_set)

	filter_geojson_features_by_graph(geojson_data, biggest_component_set)

	roadmaptools.inout.save_geojson(geojson_data, output_filepath)