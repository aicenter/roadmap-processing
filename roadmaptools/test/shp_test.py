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