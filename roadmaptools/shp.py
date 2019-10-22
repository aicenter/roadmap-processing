import math
import shapely.ops
import numpy as np

from typing import List, Union, Tuple
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


# def split(linestring: LineString, point: Point) -> List:
# 	if linestring.coords[0] == (point.x, point.y):
# 		return [None, linestring]
# 	elif linestring.coords[-1] == (point.x, point.y):
# 		return [linestring, None]
# 	else:
# 		parts = shapely.ops.split(linestring,point)
# 		if len(parts) == 1:
# 			parts = shapely.ops.split(linestring, point.buffer(config.shapely_error_tolerance))
# 		return parts

def _get_split_index(splitter_distance: float, linestring: LineString, coords) -> int:

	# portion_length = splitter_distance / linestring.length
	# index = int((len(coords) - 1) * portion_length)
	from_index = 0
	to_index = len(coords) - 1
	while True:
		index = int((to_index + from_index) / 2)
		index_point_distance = linestring.project(Point(coords[index]))
		if index_point_distance > splitter_distance:
			previous_point_distance = linestring.project(Point(coords[index - 1]))
			if previous_point_distance < splitter_distance:
				return index
			to_index = index
		else:
			next_point_distance = linestring.project(Point(coords[index + 1]))
			if next_point_distance > splitter_distance:
				return index + 1
			from_index = index


def split(linestring: LineString, point: Point) -> Union[List[LineString], LineString]:
	# if linestring.distance(point) > config.shapely_error_tolerance:
	coords = np.array(linestring.coords, dtype=object)
	if linestring.distance(point) > 0.005:
		return linestring
	if coords[0][0] == point.x and coords[0][1] == point.y:
		return [None, linestring]
	elif coords[-1][0] == point.x and coords[-1][1] == point.y:
		return [linestring, None]
	else:
		splitter_distance = linestring.project(point)
		split_index = _get_split_index(splitter_distance, linestring, coords)
		first_part_coords = linestring.coords[:split_index]
		first_part_coords.append(point)
		second_part_coords = linestring.coords[split_index:]
		second_part_coords.insert(0, (point.x, point.y))
		return [LineString(first_part_coords), LineString(second_part_coords)]


def get_remaining_linestring(linestring: LineString, point: Point) -> LineString:
	parts = split(linestring, point)
	if isinstance(parts, list):
		return parts[1]
	else:
		return parts


def extend_line(line: LineString, distance: float) -> LineString:
	first_coord = line.coords[0]
	last_coord = line.coords[-1]
	extension_point = Point(extend_vector(first_coord, last_coord, distance))
	return LineString([Point(first_coord[0], first_coord[1]), extension_point])


def extend_vector(from_coord: Tuple[float, float], to_coord: Tuple[float, float], distance: float)\
		-> Tuple[float, float]:
	length = math.sqrt(math.pow(abs(to_coord[1] - from_coord[1]), 2) + math.pow(abs(to_coord[0] - from_coord[0]), 2))
	sin = (to_coord[1] - from_coord[1]) / length
	cos = (to_coord[0] - from_coord[0]) / length
	new_length = length + distance
	new_y = from_coord[1] + sin * new_length
	new_x = from_coord[0] + cos * new_length
	extension_point = (new_x, new_y)
	return extension_point


def get_angle_between_points(point_from: Point, point_to: Point) -> float:
	y = point_to.y - point_from.y
	x = point_to.x - point_from.x

	angle = math.atan2(y, x)

	# transformation from (-pi, pi) to (0, 2pi)
	angle_trans = angle if angle > 0 else 2 * math.pi - abs(angle)

	return angle_trans


def linestring_to_points(linestring: LineString) -> List[Point]:
	points = []
	for index, x in enumerate(linestring.xy[0]):
		points.append(Point(x, linestring.xy[1][index]))

	return points