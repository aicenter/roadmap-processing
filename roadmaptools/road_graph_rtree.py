# code from https://stackoverflow.com/questions/46170577/find-closest-line-to-each-point-on-big-dataset-possibly-using-shapely-and-rtree
import geojson
import sys
import os.path

from typing import Tuple
from rtree import index
from tqdm import tqdm
from networkx import DiGraph
from shapely.geometry import Polygon, Point
from roadmaptools.printer import print_info


class RoadGraphRtree:

	def __init__(self, road_graph: DiGraph, search_size: int=500, path: str=None):
		self.search_size = search_size
		self.index = self._build_index(road_graph, path)

	@staticmethod
	def _build_index(road_graph: DiGraph, path: str=None):
		if path:
			cache_ready = os.path.isfile(path + ".idx")
			idx = index.Index(path)
		else:
			cache_ready = False
			idx = index.Index()
		if not cache_ready:
			print_info("Creating R-tree from geojson roadmap")
			for u,v,data in tqdm(road_graph.edges(data=True), desc="processing edges"):
				data["attr"]["from"] = u
				data["attr"]["to"] = v
				idx.insert(data["id"], data["attr"]["shape"].bounds, data)
			if path:
				idx.close()
				idx = index.Index(path)
		return idx

	def get_nearest_edge(self, point: Point):
		search_bounds = Point(point).buffer(self.search_size).bounds
		candidates = self.index.intersection(search_bounds, objects='raw')
		min_distance = sys.maxsize
		nearest = None
		for candidate in candidates:
			edge = candidate["attr"]
			distance = point.distance(edge["shape"])
			if distance < min_distance:
				min_distance = distance
				nearest = edge

		if not nearest:
			print_info("No edge found in specified distance ({} m).".format(self.search_size))

		envelope = Polygon(((search_bounds[0], search_bounds[3]), (search_bounds[2], search_bounds[3]),
						   (search_bounds[2], search_bounds[1]), (search_bounds[0], search_bounds[1])))
		if not envelope.intersects(nearest["shape"]):
			print_info("solution does not have to be exact")

		return nearest

