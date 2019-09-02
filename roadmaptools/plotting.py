from typing import Tuple, List, Iterable
from geojson import FeatureCollection


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
	for edge in edges_iterator:
		xlist.append(edge[0][0])
		xlist.append(edge[1][0])
		xlist.append(None)
		ylist.append(edge[0][1])
		ylist.append(edge[1][1])
		ylist.append(None)
	return xlist, ylist

