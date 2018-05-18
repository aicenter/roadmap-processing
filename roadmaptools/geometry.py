import math

from typing import Tuple


def get_distance(from_coord: Tuple[float, float], to_coord: Tuple[float, float]) -> float:
	return math.sqrt(math.pow(from_coord[0] - to_coord[0], 2) + math.pow(from_coord[1] - to_coord[1], 2))