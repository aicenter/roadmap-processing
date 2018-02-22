from roadmaptools.init import config
from shapely.geometry import Point, LineString
from shapely.geometry.base import BaseGeometry


def intersects(geometry_a: BaseGeometry, geometry_b: BaseGeometry) -> bool:
	return geometry_a.distance(geometry_b) < config.shapely_error_tolerance


def project(point: Point, linestring: LineString) -> Point:
	return linestring.interpolate(linestring.project(point))


def distance_on_linestring_between_points(linestring: LineString, point_a: Point, point_b: Point) -> float:
	return abs(linestring.project(point_a) - linestring.project(point_b))
