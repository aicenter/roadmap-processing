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
import geojson.geometry

from typing import Callable, Tuple
from shapely.geometry import LineString


def geojson_linestring_to_shp_linestring(geojson_linestring: geojson.geometry.LineString,
	coordinate_convertor: Callable[[float, float], Tuple[float, float]] = None) -> LineString:
	points = []
	for point in geojson_linestring["geometry"]["coordinates"]:
		if coordinate_convertor:
			coords = coordinate_convertor(point[1], point[0])
		else:
			coords = (point[1], point[0])
		points.append(coords)

	return LineString(points)


