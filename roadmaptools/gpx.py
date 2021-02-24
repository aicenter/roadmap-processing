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
from typing import Callable
# from gpxpy.gpx import GPX, GPXTrackPoint, GPXTrack
from gpx_lite.gpx import GPX
from gpx_lite.gpxtrackpoint import GPXTrackPoint
from gpx_lite.gpxtrack import GPXTrack
from tqdm import tqdm


def filter_gpx(gpx_content: GPX, filter: Callable[[GPXTrackPoint, GPXTrackPoint], bool]) -> GPX:
	removed_points_count = 0
	removed_segments_count = 0
	removed_tracks_count = 0

	new_tracks = []
	for track in tqdm(gpx_content.tracks, desc="Removing points using specified filter: {}".format(filter)):
		new_segments = []

		for segment in track.segments:
			new_points = []
			last_point = None
			for point in segment.points:
				if filter(last_point, point):
					new_points.append(point)
				last_point = point

			if len(new_points) < len(segment.points):
				removed_points_count += len(segment.points) - len(new_points)
				segment.points = new_points

			if len(new_points) != 0:
				new_segments.append(segment)

		if len(new_segments) < len(track.segments):
			removed_segments_count += len(track.segments) - len(new_segments)
			track.segments = new_segments

		if len(new_segments) != 0:
			new_tracks.append(track)

	if len(new_tracks) < len(gpx_content.tracks):
		removed_tracks_count += len(gpx_content.tracks) - len(new_tracks)
		gpx_content.tracks = new_tracks

	print("Removed points: {}".format(removed_points_count))
	print("Removed segments: {}".format(removed_segments_count))
	print("Removed tracks: {}".format(removed_tracks_count))

	return gpx_content


def cut_trace(trace: GPXTrack, length: int) -> GPXTrack:
	segment = trace.segments[0]
	segment.points = segment.points[:length]
	return trace