import shapely.ops

from typing import List
from roadmaptools.init import config
from shapely.geometry import Point, LineString
from shapely.geometry.base import BaseGeometry


def intersects(geometry_a: BaseGeometry, geometry_b: BaseGeometry) -> bool:
	return geometry_a.distance(geometry_b) < config.shapely_error_tolerance


def project(point: Point, linestring: LineString) -> Point:
	projected_point = linestring.interpolate(linestring.project(point))
	return projected_point


def distance_on_linestring_between_points(linestring: LineString, point_a: Point, point_b: Point) -> float:
	return abs(linestring.project(point_a) - linestring.project(point_b))


def split(linestring: LineString, point: Point) -> List:
	if linestring.coords[0] == (point.x, point.y):
		return [None, linestring]
	elif linestring.coords[-1] == (point.x, point.y):
		return [linestring, None]
	else:
		parts = shapely.ops.split(linestring,point)
		if len(parts) == 1:
			parts = shapely.ops.split(linestring, point.buffer(config.shapely_error_tolerance))
		return parts


def get_remaining_linestring(linestring: LineString, point: Point) -> LineString:
	parts = split(linestring, point)
	return parts[1] if parts[1] else parts[0]


def extend_line(line: LineString, distance: float) -> LineString:
	first_coord = line.coords[0]
	last_coord = line.coords[-1]
	sin = abs(first_coord[1] - last_coord[1]) / line.length
	cos = abs(first_coord[0] - last_coord[0]) / line.length
	new_length = line.length + distance
	new_b = sin * new_length
	new_a = cos * new_length
	extension_point = Point(first_coord[0] + new_a, first_coord[1] + new_b)
	return LineString([Point(first_coord[0], first_coord[1]), extension_point])