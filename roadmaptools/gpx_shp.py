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
