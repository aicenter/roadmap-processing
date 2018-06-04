import geojson.geometry
import roadmaptools.geojson_shp
import roadmaptools.utm

from typing import Callable, Tuple
from shapely.geometry import Point


class Node:
	def __init__(self, x: float, y: float, id: int):
		self.id = id
		self.x = x
		self.y = y
		self._point = None

	def get_point(self) -> Point:
		if not self._point:
			self._point = Point(self.x, self.y)

		return self._point

	def __eq__(self, o: object) -> bool:
		if isinstance(o, self.__class__):
			return self.id == o.id
		return False

	def __ne__(self, o: object) -> bool:
		if isinstance(o, self.__class__):
			return self.id != o.id
		return False

	def __hash__(self) -> int:
		return hash(self.id)


class LinestringEdge:

	def __init__(self, geojson_linestring: geojson.geometry.LineString,
				 coordinate_convertor: Callable[[float, float], Tuple[float, float]], node_from: Node, node_to: Node):
		self.geojson_linestring = geojson_linestring
		self.linestring = roadmaptools.geojson_shp.geojson_linestring_to_shp_linestring(geojson_linestring,
																							coordinate_convertor)
		self.node_from = node_from
		self.node_to = node_to
		self.id = str(node_from.id) + "-" + str(node_to.id)

	def __eq__(self, o: object) -> bool:
		if isinstance(o, self.__class__):
			return self.id == o.id
		return False

	def __ne__(self, o: object) -> bool:
		if isinstance(o, self.__class__):
			return self.id != o.id
		return False

	def __hash__(self) -> int:
		return hash(self.id)



