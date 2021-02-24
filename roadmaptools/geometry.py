#
# Copyright (c) 2021 Czech Technical University in Prague.
#
# This file is part of Roadmaptools 
# (see https://github.com/aicenter/roadmap-processing).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
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

