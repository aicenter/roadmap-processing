from typing import Callable
from gpxpy.gpx import GPXTrack
from shapely.geometry import LineString


def track_to_linestring(track: GPXTrack, coordinate_convertor: Callable[[float, float], (float, float)] = None)\
		-> LineString:
	points = []
	for segment in track.segments:
		for point in segment.points:
			coords = (point.latitude, point.longitude)
			if coordinate_convertor:
				coords = coordinate_convertor(coords)
			points.append(coords)

	return LineString(points)