from roadmaptools.init import config
from shapely.geometry.base import BaseGeometry


def intersects(geometry_a: BaseGeometry, geometry_b: BaseGeometry) -> bool:
	return geometry_a.distance(geometry_b) < config.shapely_error_tolerance
