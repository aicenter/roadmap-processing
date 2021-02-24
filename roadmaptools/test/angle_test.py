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
import roadmaptools.shp

from shapely.geometry import Point, LineString

# angle = roadmaptools.shp.get_angle_between_points(Point(0, 0), Point(-1, -1))
#
# print(angle)

mu_alpha = 50
n_alpha = 3

def get_angle_difference(current_point: Point, previous_point: Point, edge: LineString) -> float:
	trace_angle = roadmaptools.shp.get_angle_between_points(previous_point, current_point)
	edge_angle = roadmaptools.shp.get_angle_between_points(Point(edge.coords[0]), Point(edge.coords[-1]))
	angle_diff = abs(trace_angle - edge_angle)
	return angle_diff

def _get_orientation_measure(current_point: Point, previous_point: Point, edge: LineString):
	angle_diff = get_angle_difference(current_point, previous_point, edge)
	return mu_alpha * math.pow(math.cos(angle_diff), n_alpha)

a = Point(0,0)
b = Point(0,1)
line = LineString([(0,0), (0,1)])

print(get_angle_difference(a, b, line))
print(_get_orientation_measure(a, b, line))


