from setuptools.command.rotate import rotate

import roadmaptools.utm

from typing import Tuple, List, Iterable
from geojson import FeatureCollection

from roadmaptools.utm import TransposedUTM


def geojson_iterator(fc: FeatureCollection) -> Iterable[Tuple[Tuple[float, float],Tuple[float, float]]]:
	for edge in fc['features']:
		from_coords = None
		for coordinates in edge['geometry']['coordinates']:
			to_coords = coordinates
			if from_coords:
				yield (([from_coords[0], from_coords[1]]),([to_coords[0], to_coords[1]]))
			from_coords = to_coords


def export_for_matplotlib(edges_iterator: Iterable[Tuple[Tuple[float, float],Tuple[float, float]]])\
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

