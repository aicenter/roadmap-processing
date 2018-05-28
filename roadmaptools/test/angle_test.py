import roadmaptools.shp

from shapely.geometry import Point

angle = roadmaptools.shp.get_angle_between_points(Point(0, 0), Point(-1, -1))

print(angle)
