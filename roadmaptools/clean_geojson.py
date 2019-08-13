import geojson
import codecs
import copy
import argparse
import sys
import time
import pandas as pd
import roadmaptools.inout
import roadmaptools.road_structures

from typing import Dict, Set, List
from tqdm import tqdm, trange
from geojson import FeatureCollection, Feature
from pandas import DataFrame
from roadmaptools.printer import print_info
from roadmaptools.init import config

# properties that will not be deleted
SET_OF_USEFUL_PROPERTIES = {'highway', 'id', 'lanes', 'maxspeed', 'oneway', 'bridge', 'width', 'tunnel',
							'traffic_calming', 'lanes:forward', 'lanes:backward', 'junction'}

# for correct type conversion
dict_of_useful_properties = {'highway': str, 'id': int, 'lanes': int, 'maxspeed': int, 'oneway': str, 'bridge': str,
							 'width': float, 'tunnel': str, 'traffic_calming': str, 'lanes:forward': int,
							 'lanes:backward': int, 'junction': str}

nonempty_columns = set()


def clean_geojson_files(input_file_path: str = config.geojson_file, output_file_path: str = config.cleaned_geojson_file,
						keep_attributes: Set[str] = SET_OF_USEFUL_PROPERTIES, remove_attributes: Set[str] = None):
	print_info('Cleaning geoJSON - input file: {}, cleaned file: {}'.format(input_file_path, output_file_path))

	start_time = time.time()
	feature_collection = roadmaptools.inout.load_geojson(input_file_path)
	prune_geojson_file(feature_collection, keep_attributes, remove_attributes)

	print_info('Cleaning complete. (%.2f secs)' % (time.time() - start_time))

	roadmaptools.inout.save_geojson(feature_collection, output_file_path)


def clean_geojson(input_stream, output_stream):
	json_dict = _load_geojson(input_stream)
	json_deleted = get_geojson_with_deleted_features(json_dict)
	# save_geojson(output_stream, json_deleted)
	prune_geojson_file(json_dict)
	save_geojson(json_dict, output_stream)


# def get_cleaned_geojson(json_dict):
# 	print_info("Cleaning geojson")
# 	prune_geojson_file(json_dict)
# 	print_info("Removing empty features")
# 	json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
# 	return json_dict


def remove_properties(item, keep_attributes: Set[str], remove_attributes: Set[str]) -> Feature:
	# temp_dict_with_props = copy.deepcopy(item['properties'])
	# for prop in temp_dict_with_props:
	# 	if prop not in set_of_useful_properties:
	# 		del item['properties'][prop]

	if remove_attributes:
		item['properties'] = {k: v for k, v in item['properties'].items() if k not in remove_attributes}
	else:
		item['properties'] = {k: v for k, v in item['properties'].items() if k in keep_attributes}
	return item


def _load_geojson(in_stream):
	json_dict = geojson.load(in_stream)
	return json_dict


def get_geojson_with_deleted_features(json_dict):
	json_deleted = dict()
	json_deleted['type'] = json_dict['type']
	json_deleted['features'] = list()

	for item in json_dict['features']:
		if item['geometry']['type'] != 'LineString':
			json_deleted['features'].append(item)

	# with codecs.open("data/deleted_items.geojson", 'w') as output:
	#     geojson.dump(json_deleted, output)
	# output.close()
	return json_deleted


def create_desimplified_edge(coord_u, coord_v, item: Feature, is_forward: bool):
	item['properties']['id'] = str(roadmaptools.road_structures.get_edge_id_from_coords(coord_u, coord_v))
	del item['geometry']['coordinates']
	item['geometry']['coordinates'] = [coord_u, coord_v]

	# lane config for two way roads
	if 'oneway' not in item['properties'] or item['properties']['oneway'] != 'yes':
		if 'lanes:forward' in item['properties'] and is_forward:
			item['properties']['lanes'] = int(item['properties']['lanes:forward'])
		elif 'lanes:backward' in item['properties'] and not is_forward:
			item['properties']['lanes'] = int(item['properties']['lanes:backward'])
		# elif is_forward and 'lanes' in item['properties']:
		# 	item['properties']['lanes'] = int(item['properties']['lanes']) - 1
		# elif not is_forward and 'lanes' in item['properties']:
		# 	item['properties']['lanes'] = 1
		elif 'lanes' in item['properties'] and int(item['properties']['lanes']) >= 2:
			item['properties']['lanes'] = int(item['properties']['lanes']) / 2
		else:
			item['properties']['lanes'] = 1
	# lane config for one way roads
	else:
		if 'lanes' not in item['properties'] or int(item['properties']['lanes']) < 1:
			item['properties']['lanes'] = 1
		else:
			item['properties']['lanes'] = int(item['properties']['lanes'])

	# item['properties']['oneway'] = 'yes'
	return item


def check_types(item: Feature):
	for prop in dict_of_useful_properties:
		if prop in item['properties'] and not isinstance(item['properties'][prop], dict_of_useful_properties[prop]):
			if dict_of_useful_properties[prop] == int:
				try:
					if " mph" in item['properties'][prop]:
						temp = item['properties'][prop].split()
						item['properties'][prop] = float(temp[0]) * 1.609344
					elif " knots" in item['properties'][prop]:
						temp = item['properties'][prop].split()
						item['properties'][prop] = float(temp[0]) * 1.85200
					else:
						int(item['properties'][prop])
				except:
					del item['properties'][prop]
			elif dict_of_useful_properties[prop] == str:
				try:
					str(item['properties'][prop])
				except:
					del item['properties'][prop]
			elif dict_of_useful_properties[prop] == int:
				try:
					int(item['properties'][prop])
				except:
					del item['properties'][prop]
			elif dict_of_useful_properties[prop] == float:
				try:
					if " m" in item['properties'][prop]:
						temp = item['properties'][prop].split()
						item['properties'][prop] = float(temp[0])
					elif " km" in item['properties'][prop]:
						temp = item['properties'][prop].split()
						item['properties'][prop] = float(temp[0]) * 1000
					elif " mi" in item['properties'][prop]:
						temp = item['properties'][prop].split()
						item['properties'][prop] = float(temp[0]) * 1609.344
					else:
						float(item['properties'][prop])
				except:
					del item['properties'][prop]


def prune_geojson_file(json_dict: FeatureCollection, keep_attributes: Set[str], remove_attributes: Set[str],
					   desimplify=True):
	"""
	Transforms the geojson file into the version to be used with roadmaptools.
	Output file contains only edges. Each edge receives an id, starting from 0 to edge count.
	Feature collection is changed inplace.

	If desimplify=True, than the edges are split on coordinates. Note that this is usually needed even when we
	want the graph to be simplified, because in raw data from openstreetmap, the roads are not split on crossroads.

	:param json_dict: Input data
	:param keep_attributes: edge attributes to keep
	:param remove_attributes: edge attributes to remove
	:param desimplify: True, means than the edges are split on coordinates.
	:return: None, the feature collection is changed in place
	"""

	edges = [item for item in json_dict['features'] if item['geometry']['type'] == 'LineString']

	json_dict['features'] = []

	for item in tqdm(edges, desc="Pruning geojson"):
		remove_properties(item, keep_attributes, remove_attributes)
		# check_types(item)
		if desimplify:
			for j in range(0, len(item['geometry']['coordinates']) - 1):
				new_edge = copy.deepcopy(item)
				u = item['geometry']['coordinates'][j]
				v = item['geometry']['coordinates'][j + 1]
				new_item = create_desimplified_edge(u, v, new_edge, True)
				json_dict['features'].append(new_item)

				# create the opposite direction edge if it is not oneway
				if 'oneway' not in item['properties'] or item['properties']['oneway'] != 'yes':
					new_edge = copy.deepcopy(item)
					new_item = create_desimplified_edge(v, u, new_edge, False)
					json_dict['features'].append(new_item)


def save_geojson(json_dict, out_stream):
	json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
	geojson.dump(json_dict, out_stream)


def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
	parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
	return parser.parse_args()


def get_non_empty_columns(edges: List[Feature], empty_ratio: float = 0) -> Set[str]:

	# dataframe init
	rows = []
	for item in tqdm(edges, desc="Counting non-empty properties"):
		row = item['properties']
		rows.append(row)
	table = DataFrame.from_records(rows)

	nonempty_columns = set()
	columns = set()

	for column in table.columns:
		non_empty_count = count_nonempty_in_column(table, column)
		ratio = non_empty_count / len(table)
		if ratio > empty_ratio:
			nonempty_columns.add(column)
		columns.add(column)

	print("removed {} empty columns".format(len(columns) - len(nonempty_columns)))

	return nonempty_columns


def count_nonempty_in_column(dataframe: DataFrame, column: str) -> int:
	return (dataframe[column].values != '').sum()

# EXAMPLE OF USAGE
if __name__ == '__main__':
	args = get_args()
	input_stream = sys.stdin
	output_stream = sys.stdout

	if args.input is not None:
		input_stream = codecs.open(args.input, encoding='utf8')
	if args.output is not None:
		output_stream = codecs.open(args.output, 'w')

	clean_geojson(input_stream, output_stream)
	input_stream.close()
	output_stream.close()
