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


