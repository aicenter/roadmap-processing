from typing import Callable, Tuple
# from gpxpy.gpx import GPXTrack, GPXTrackPoint
from gpx_lite.gpxtrack import GPXTrack
from gpx_lite.gpxtrackpoint import GPXTrackPoint
from shapely.geometry import LineString, Point


def track_to_linestring(track: GPXTrack, coordinate_convertor: Callable[[float, float], Tuple[float, float]] = None) \
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


def trackpoint_to_point(trackpoint: GPXTrackPoint,
                        coordinate_convertor: Callable[[float, float], Tuple[float, float]] = None) -> Point:
    if coordinate_convertor:
        coords = coordinate_convertor(trackpoint.latitude, trackpoint.longitude)
    else:
        coords = (trackpoint.latitude, trackpoint.longitude)
    return Point(*coords)
