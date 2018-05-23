import networkx.algorithms.shortest_paths
import roadmaptools.utm
import roadmaptools.geometry
import roadmaptools.shp

from typing import Dict, Union, Optional
from networkx import DiGraph
from shapely.geometry import Point
from scipy.spatial.kdtree import KDTree
from geojson import FeatureCollection
from tqdm import tqdm
from roadmaptools.printer import print_info
from roadmaptools.road_structures import LinestringEdge, Node
from roadmaptools.utm import CoordinateConvertor


def get_node_id(node) -> str:
	lon = int(node[0] * 10 ** 6)
	lat = int(node[1] * 10 ** 6)
	if lon < 0 and lat < 0:
		return "1" + str(lon)[1:] + str(lat)[1:]
	elif lon < 0 and lat >= 0:
		return "2" + str(lon)[1:] + str(lat)
	elif lon >= 0 and lat < 0:
		return "3" + str(lon) + str(lat)[1:]
	else:
		return str(lon) + str(lat)


class RoadGraph:

	def __init__(self):
		self.graph: DiGraph = DiGraph()
		self.kdtree: KDTree = None
		self.projection = None
		self.node_map: Dict[int, Node] = {}

	def load_from_geojson(self, geojson: FeatureCollection):

		# projection determination
		first_coord = geojson['features'][0]['geometry']['coordinates']
		self.projection = roadmaptools.utm.TransposedUTM(first_coord[1], first_coord[0])
		print_info("Projection determined from the first coordinate: {}{}".format(
			self.projection.origin_zone_number, self.projection.origin_zone_letter))
		CoordinateConvertor.projection = self.projection

		print_info("Creating networkx graph from geojson")
		for item in tqdm(geojson['features'], desc="processing features"):
			if item["geometry"]["type"] == "LineString":
				coords = item['geometry']['coordinates']
				coord_from = roadmaptools.utm.wgs84_to_utm(coords[0][1], coords[0][0], self.projection)
				coord_to = roadmaptools.utm.wgs84_to_utm(coords[-1][1], coords[-1][0], self.projection)

				node_from = self._get_node(coord_from[0], coord_from[1])
				node_to = self._get_node(coord_to[0], coord_to[1])

				edge = LinestringEdge(item, CoordinateConvertor.convert, node_from, node_to)

				# TODO legacy, remove after moving id from properties to id attribute
				edge_id = item['properties']['id'] if "id" in item['properties'] else item['id']
				length = item['properties']['length'] if 'length' in item['properties'] \
					else roadmaptools.geometry.get_distance(coord_from, coord_to)
				self.graph.add_edge(node_from, node_to, id=edge_id, length=length, edge=edge)

	def _get_node(self, x: float, y: float) -> Node:
		id = roadmaptools.utm.get_id_from_utm_coords(x, y)
		if id in self.node_map:
			return self.node_map[id]
		else:
			node = self._create_node(x, y, id)
			self.node_map[id] = node
			return node

	@staticmethod
	def _create_node(x: float, y: float, id: int) -> Node:
		return Node(x, y, id)

	def get_precise_path_length(self, edge_from: LinestringEdge, edge_to: LinestringEdge, 
								point_from: Point, point_to: Point) -> Optional[float]:
		from_node = edge_from.node_to
		to_node = edge_to.node_from
		
		if edge_from == edge_to:
			length = roadmaptools.shp.distance_on_linestring_between_points(edge_from.linestring, point_from, point_to)
		else:
			try:
				length = networkx.algorithms.shortest_paths.astar_path_length(self.graph, from_node, to_node, weight="length")
			except networkx.exception.NetworkXNoPath:
				return None

			length += edge_from.linestring.length - edge_from.linestring.project(point_from)
			length += edge_to.linestring.project(point_to)

		return length

	def _get_node_for_path_search(self, edge_from, point_from):
		pass
