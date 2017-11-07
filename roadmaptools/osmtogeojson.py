from osmread import parse_file, Node, Way
import geojson
from geojson import Point, LineString, Feature, FeatureCollection
import argparse
import sys
import codecs
import time

from tqdm import tqdm
from roadmaptools.init import config
from roadmaptools.printer import print_info

dict_of_coords = dict()


def convert_osm_to_geojson():
	input_file = config.filtered_osm_filename
	output_file = config.geojson_file

	print_info('Converting from OSM format to geoJSON - input file: {}, output file: {}'.format(input_file, output_file))
	start_time = time.time()

	geojson_file = convert_osmtogeojson(input_file)
	f = open(output_file, 'w')
	save_geojson(geojson_file, f)
	print_info("Geojson saved successfully to {}".format(output_file))
	f.close()

	print_info('Converting from OSM to geoJSON finished. (%.2f secs)' % (time.time() - start_time))


def convert_osmtogeojson(filename):
	_get_all_coordinates(filename)

	feature_collection = []

	for item in parse_file(filename):  # generator!!
		if isinstance(item, Node) and item.tags != {}:
			point = Point(dict_of_coords[item.id])
			feature = Feature(geometry=point, id=item.id, properties=item.tags)
			feature_collection.append(feature)
		elif isinstance(item, Way) and 'highway' in item.tags:
			coords = _get_coords_of_edge(item.nodes)
			line_string = LineString(coords)
			feature = Feature(geometry=line_string, id=item.id, properties=item.tags)
			feature_collection.append(feature)

		print_info("\rParsing features - feature count: {:,}".format(len(feature_collection)).replace(",", " "),
				   end='')
	print("")

	geojson_file = FeatureCollection(feature_collection)

	# with open('data/output.geojson', 'w') as outfile:
	#     geojson.dump(geojson_file, outfile)
	# outfile.close()
	return geojson_file


def _get_all_coordinates(filename):
	for item in parse_file(filename):  # generator!!
		if isinstance(item, Node):
			dict_of_coords[item.id] = (item.lon, item.lat)
			print_info("\rParsing all coordinates - node count: {:,}".format(len(dict_of_coords)).replace(",", " "),
					   end='')
	print("")


def _get_coords_of_edge(nodes):
	loc_coords = []
	for node in nodes:
		try:
			loc_coords.append(dict_of_coords[node])
		except:
			# print("this node_id {} is required, but not found in OSM!".format(node),file=sys.stderr)
			pass
	return loc_coords



def is_geojson_valid(geojson_file):
	validation = geojson.is_valid(geojson_file)
	return validation['valid']


def save_geojson(json_dict, out_stream):
	geojson.dump(json_dict, out_stream)


def get_args():
	parser = argparse.ArgumentParser()
	#    parser.add_argument('map', type=str, help="map in OSM format")
	parser.add_argument('--version', action='version', version='%(prog)s 0.1.2')
	parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
	parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
	return parser.parse_args()


if __name__ == '__main__':
	args = get_args()
	output_stream = sys.stdout

	if args.input is not None:
		input_stream = codecs.open(args.input, encoding='utf8')
	else:
		exit(1)
	if args.output is not None:
		output_stream = codecs.open(args.output, 'w')

	geojson_file = convert_osmtogeojson(args.input)
	save_geojson(geojson_file, output_stream)
