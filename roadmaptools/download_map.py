from roadmaptools.init import config

import roadmaptools.inout
import overpass

from typing import Tuple, List
from roadmaptools.printer import print_info


HIGHWAY_FILTER = 'highway~"(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link|tertiary|tertiary_link|unclassified|unclassified_link|residential|residential_link|living_street)"'


def download_cities(bounding_boxes: List[Tuple[float, float, float, float]], filepath: str):
	"""
	Downloads osm map and saves it as .geojson file.
	:param bounding_boxes: Order of coordinates in bounding box: (min lat, min lon, max lan, max lon)
	:param filepath: path to output file
	:return:
	"""
	print_info("Downloading map from Overpass API")
	api = overpass.API(debug=True, timeout=600)
	query = '(('

	for bounding_box in bounding_boxes:
		if float(bounding_box[0]) >= float(bounding_box[2]) or float(bounding_box[1]) >= float(bounding_box[3]):
			raise Exception('Wrong order in: ', bounding_box)
		query += 'way({})[{}][access!="no"];'.format(",".join(map(str, list(bounding_box))), HIGHWAY_FILTER)

	query += ')->.edges;.edges >->.nodes;);'
	out = api.get(query, verbosity='geom')
	roadmaptools.inout.save_geojson(out, filepath)


if __name__ == '__main__':
	# download_cities([(49.94, 14.22, 50.17, 14.71), (49.11, 16.42, 49.30,16.72)], "test.geojson")
	download_cities([(envelope["south"], envelope["east"], envelope["north"], envelope["west"]) for _, envelope in config.cities_envelopes.items()] , config.geojson_file)