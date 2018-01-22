from typing import Callable, Tuple
from gpxpy.gpx import GPXTrack
from shapely.geometry import LineString


def track_to_linestring(track: GPXTrack, coordinate_convertor: Callable[[float, float], Tuple[float, float]] = None)\
		-> LineString:
	points = []
	for segment in track.segments:
		for point in segment.points:
			if coordinate_convertor:
				coords = coordinate_convertor(point.latitude, point.longitude)
			else:
				coords = (point.latitude, point.longitude)
			points.append(coords)

	return LineString(points)