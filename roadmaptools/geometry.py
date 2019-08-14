import math

from typing import Tuple


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