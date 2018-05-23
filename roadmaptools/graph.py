from networkx import DiGraph
from shapely.geometry import Point
from scipy.spatial.kdtree import KDTree
from roadmaptools.road_structures import LinestringEdge


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
		self.graph: DiGraph = None
		self.kdtree: KDTree = None

	def get_precise_path_length(self, edge_from: LinestringEdge, edge_to: LinestringEdge, 
								point_from: Point, point_to: Point):
		from_node = self._get_node_for_path_search(edge_from, point_from)

	def _get_node_for_path_search(self, edge_from, point_from):
		pass
