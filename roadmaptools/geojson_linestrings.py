from typing import List, Iterable
from geojson import LineString, MultiLineString


def merge_linestrings(linestrings: Iterable[LineString]) -> MultiLineString:
	linestrings_coords = []
	for linestring in linestrings:
		linestrings_coords.append(linestring["geometry"]["coordinates"])

	return MultiLineString(linestrings_coords)