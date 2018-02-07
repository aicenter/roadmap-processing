import networkx as nx
import roadmaptools.inout

from networkx import MultiDiGraph
from geojson.feature import FeatureCollection
from tqdm import tqdm
from roadmaptools.init import config
from roadmaptools.printer import print_info


def get_biggest_component(graph: MultiDiGraph) -> set:
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


def sanitize():
	geojson_data = roadmaptools.inout.load_geojson(config.cleaned_geojson_file)

	graph = roadmaptools.inout.load_graph(geojson_data)
	graph = get_biggest_component(graph)

	filter_geojson_features_by_graph(geojson_data, graph)

	roadmaptools.inout.save_geojson(geojson_data, config.sanitized_geojson_file)