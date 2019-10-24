
from typing import Callable
from geojson import FeatureCollection


def filter_edges(edges: FeatureCollection, filter: Callable[[dict], bool]):
	filtered_edges = []
	for edge in edges['features']:
		if filter(edge):
			filtered_edges.append(edge)

	edges['features'] = filtered_edges
