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
from setuptools.command.rotate import rotate

import roadmaptools.utm

from typing import Tuple, List, Iterable
from geojson import FeatureCollection

from roadmaptools.utm import TransposedUTM


def geojson_edges_iterator(fc: FeatureCollection) -> Iterable[Tuple[Tuple[float, float], Tuple[float, float]]]:
	for f in fc['features']:
		if f["geometry"]["type"] == "LineString":
			from_coords = None
			for coordinates in f['geometry']['coordinates']:
				to_coords = coordinates
				if from_coords:
					yield (([from_coords[0], from_coords[1]]),([to_coords[0], to_coords[1]]))
				from_coords = to_coords


def geojson_node_iterator(fc: FeatureCollection) -> Iterable[Tuple[float, float]]:
	for f in fc['features']:
		if f["geometry"]["type"] == "Point":
			coordinates = f['geometry']['coordinates']
			yield (coordinates[0], coordinates[1])


def export_nodes_for_matplotlib(nodes_iterator: Iterable[Tuple[float, float]])\
		-> Tuple[List[float], List[float]]:
	xlist = []
	ylist = []
	projection = None
	for point in nodes_iterator:
		if not projection:
			projection = roadmaptools.utm.TransposedUTM.from_gps(point[0], point[1])
		coords = roadmaptools.utm.wgs84_to_utm(point[0], point[1], projection)
		xlist.append(coords[0])
		ylist.append(coords[1])
	return xlist, ylist


def export_edges_for_matplotlib(edges_iterator: Iterable[Tuple[Tuple[float, float], Tuple[float, float]]])\
		-> Tuple[List[float], List[float]]:
	xlist = []
	ylist = []
	projection = None
	for edge in edges_iterator:
		if not projection:
			projection = roadmaptools.utm.TransposedUTM.from_gps(edge[0][1], edge[0][0])
		from_coords = roadmaptools.utm.wgs84_to_utm(edge[0][1], edge[0][0], projection)
		to_coords = roadmaptools.utm.wgs84_to_utm(edge[1][1], edge[1][0], projection)
		xlist.append(from_coords[0])
		xlist.append(to_coords[0])
		xlist.append(None)
		ylist.append(from_coords[1])
		ylist.append(to_coords[1])
		ylist.append(None)
	return xlist, ylist

