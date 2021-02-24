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
import roadmaptools.shp

from shapely.geometry import LineString, Point

point = Point(2,1)
line_split = LineString([Point(1, 1), Point(3, 1)])
line = LineString([(0,3),(4,3),(2,6),(2,0)])
from shapely.ops import split
splitted = split(line, point)
for lin in splitted:
      print(lin)

splitted = roadmaptools.shp.split(line, point)

for lin in splitted:
      print(lin)

# line = LineString([(1,1), (0, 5)])
# ref_point = Point(0,10)
# extended_line = roadmaptools.shp.extend_line(line, 8)
# print(extended_line)
# # print(LineString(line.coords.append(ref_point)))