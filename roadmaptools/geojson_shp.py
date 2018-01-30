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


