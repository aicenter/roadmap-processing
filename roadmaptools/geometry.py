import math

from typing import Tuple, List


def get_distance(from_coord: Tuple[float, float], to_coord: Tuple[float, float]) -> float:
	return math.sqrt(math.pow(from_coord[0] - to_coord[0], 2) + math.pow(from_coord[1] - to_coord[1], 2))


def get_distance_int(from_coord: Tuple[int, int], to_coord: Tuple[int, int]) -> int:
	"""
	Compute integer distance in from utm/cartesian coordinates supplied as integer.
	:param from_coord: UTM coord from.
	:param to_coord: UTM coord to.
	:return: Distance as integer.
	"""
	return int(round(get_distance(from_coord, to_coord)))


def get_length_from_coords(coords: List[Tuple[int,int]]) -> int:
	length = 0
	for i in range(0, len(coords) - 1):
		from_coord = coords[i]
		to_coord = coords[i + 1]
		length += get_distance_int(from_coord, to_coord)

	return length

