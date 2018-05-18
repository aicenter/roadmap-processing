import geojson.geometry
import roadmaptools.geojson_shp
import roadmaptools.utm

from typing import Callable, Tuple
from shapely.geometry import Point


class LinestringEdge:

	def __init__(self, geojson_linestring: geojson.geometry.LineString,
				 coordinate_convertor: Callable[[float, float], Tuple[float, float]]):
		self.geojson_linestring = geojson_linestring
		self.linestring = roadmaptools.geojson_shp.geojson_linestring_to_shp_linestring(geojson_linestring,
			coordinate_convertor)


class Node:
	def __init__(self, x: int, y: int, id: int):
		self.id = id
		self.x = x
		self.y = y
		self._point = None

	def get_point(self) -> Point:
		if not self._point:
			self._point = Point(self.x, self.y)

		return self._point

