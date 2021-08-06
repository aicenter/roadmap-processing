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
from roadmaptools.init import config

import roadmaptools.inout
import overpass
import osm2geojson

from typing import Tuple, List
from roadmaptools.printer import print_info


WAY_FILTER = """
	[highway~"(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link|tertiary|tertiary_link|unclassified|unclassified_link|residential|residential_link|living_street)"]
	[access!="no"]
"""


def _convert_json_to_geojson(json):

	# way to node list dict
	node_dict = {}
	for el in json['elements']:
		if el['type'] == 'way':
			node_dict[el['id']] = el['nodes']

	geojson = osm2geojson.json2geojson(json)

	# converting geojson to desired format
	for feature in geojson['features']:
		if feature['geometry']['type'] == 'LineString':
			feature['id'] = feature['properties']['id']
			del feature['properties']['id']
			for key, val in feature['properties']['tags'].items():
				feature['properties'][key] = val
			del feature['properties']['tags']
			feature['properties']['nodes'] = node_dict[feature['id']]

	return geojson


def call_overpass(query: str, filepath: str):
	print_info("Downloading map from Overpass API")
	api = overpass.API(debug=True, timeout=600)
	out = api.get(query, verbosity='geom', responseformat="json")
	roadmaptools.inout.save_geojson(_convert_json_to_geojson(out), filepath)


def download_cities(bounding_boxes: List[Tuple[float, float, float, float]], filepath: str):
	"""
	Downloads osm map and saves it as .geojson file.
	:param bounding_boxes: Order of coordinates in bounding box: (min lat, min lon, max lan, max lon)
	:param filepath: path to output file
	:return:
	"""

	query = '(('

	for bounding_box in bounding_boxes:
		if float(bounding_box[0]) >= float(bounding_box[2]) or float(bounding_box[1]) >= float(bounding_box[3]):
			raise Exception('Wrong order in: ', bounding_box)
		query += 'way({}){};'.format(",".join(map(str, list(bounding_box))), WAY_FILTER)

	query += ')->.edges;.edges >->.nodes;);'
	call_overpass(query, filepath)


def download_by_name(name: str, filepath: str):
	"""
	Downloads osm map and saves it as .geojson file.
	:param name: Name of the area on Open Street Map
	:param filepath: path to output file
	:return:
	"""
	query = """
	area[name="{}"];
	((
		way(area)
			{};)->.edges;.edges >->.nodes;);""".format(name, WAY_FILTER)
	call_overpass(query, filepath)


if __name__ == '__main__':
	# download_cities([(49.94, 14.22, 50.17, 14.71), (49.11, 16.42, 49.30,16.72)], "test.geojson")
	download_cities([(envelope["south"], envelope["east"], envelope["north"], envelope["west"]) for _, envelope in config.cities_envelopes.items()] , config.geojson_file)