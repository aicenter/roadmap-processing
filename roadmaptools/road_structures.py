import geojson.geometry
import roadmaptools.geojson_shp
import roadmaptools.utm

from typing import Callable, Tuple, TypeVar
from shapely.geometry import Point


T = TypeVar('T', int, float, str)


def get_node_id(lat: T, lon: T) -> int:

	# convert to integer E6 format
	if isinstance(lat, str):
		try:
			lat = int(lat)
			lon = int(lon)
		except ValueError:
			lat = float(lat)
			lon = float(lon)
	if isinstance(lat, float):
		lat = int(lat * 10 ** 7)
		lon = int(lon * 10 ** 7)

	# compute prefix marking a sign
	if lon < 0 and lat < 0:
		prefix = 0
	elif lon < 0 and lat >= 0:
		prefix = 1
	elif lon >= 0 and lat < 0:
		prefix = 2
	else:
		prefix = 3

	string_id = "{}{:010}{:010}".format(prefix, abs(lat), abs(lon))

	return int(string_id)


def get_edge_id(id_from: int, id_to: int) -> int:
	return int("{}{}".format(id_from, id_to))


def get_edge_id_from_coords(from_coord: Tuple[T, T], to_coord: Tuple[T, T]) -> int:
	from_id = get_node_id(*from_coord)
	to_id = get_node_id(*to_coord)
	return get_edge_id(from_id, to_id)


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
		self.id = get_edge_id(node_from.id, node_to.id)

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



