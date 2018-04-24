import urllib.request
import os
import bz2
import sys
import pickle
import json
import geojson
import geojson.feature
import networkx as nx
import csv
import gpxpy
import gpxpy.gpx

from typing import Iterable, Callable, Dict, Tuple, List, Union
from tqdm import tqdm
from logging import info
from gpxpy.gpx import GPX
from roadmaptools.init import config
from roadmaptools.printer import print_info


class Progressbar(tqdm):
	"""Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""

	def update_to(self, b=1, bsize=1, tsize=None):
		"""
		b  : int, optional
			Number of blocks transferred so far [default: 1].
		bsize  : int, optional
			Size of each block (in tqdm units) [default: 1].
		tsize  : int, optional
			Total size (in tqdm units). If [default: None] remains unchanged.
		"""

		if tsize is not None:
			self.total = tsize
		self.update(b * bsize - self.n)  # will also set self.n = b * bsize


def download_file(url: str, file_name: str):
	print_info("Downloading file from {} to {}".format(url, file_name))
	with Progressbar(unit='B', unit_scale=True, miniters=1, desc="Downloading file") as progressbar:
		urllib.request.urlretrieve(url, file_name, progressbar.update_to)

	print_info("Download finished")


def extract_file(filename: str):
	new_filename = filename.replace(".bz2", "")
	compressed_size = os.path.getsize(filename)
	print_info("Extracting file {} to {} (compressed size: {})".format(filename, new_filename, compressed_size))

	block_size = 100 * 1024
	uncompressed_size = 0
	with open(new_filename, 'wb') as new_file, bz2.BZ2File(filename, 'rb') as file:
		for data in iter(lambda: file.read(block_size), b''):
			new_file.write(data)
			uncompressed_size += block_size
			print_info("\rDecompressing - decompressed size: {:,}B".format(uncompressed_size).replace(",", " "), end='')
	uncompressed_size = os.path.getsize(new_filename)
	print_info("\nExtraction finished: uncompressed size: {:,}B".format(uncompressed_size).replace(",", " "))


def get_osm_from_mapzen():
	print_info("Getting map from mapzen.")
	download_file(config.osm_source_url, config.osm_map_filename + ".bz2")
	extract_file(config.osm_map_filename + ".bz2")
	print_info("Map from mapzen ready.")


def load_json(filepath: str) -> Union[Dict, List]:
	print_info("Loading json file from: {}".format(os.path.realpath(filepath)))
	return json.load(open(filepath))


def load_geojson(filepath: str) -> geojson.feature.FeatureCollection:
	print_info("Loading geojson file from: {}".format(os.path.realpath(filepath)))
	input_stream = open(filepath, encoding='utf8')
	json_dict = geojson.load(input_stream)
	return json_dict


def save_geojson(data: geojson.feature.FeatureCollection, filepath: str):
	print_info("Saving geojson file to: {}".format(filepath))
	out_stream = open(filepath, 'w')
	geojson.dump(data, out_stream)


def load_csv(filepath: str, delimiter: str = ",") -> Iterable:
	print_info("Loading csv file from: {}".format(os.path.realpath(filepath)))
	f = open(filepath, "r")
	return csv.reader(f, delimiter=delimiter)


def save_csv(data: List[List[str]], filepath: str):
	with open(filepath, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)
		for row in data:
			writer.writerow(row)


def save_gpx(data: GPX, filepath: str):
	print_info("Saving GPX file to: {}".format(os.path.realpath(filepath)))
	with open(filepath, 'w') as outfile:
		outfile.write(data.to_xml())
	print_info("{} tracks saved".format(len(data.tracks)))


def load_gpx(filepath: str) -> GPX:
	print_info("Loading GPX file from: {}".format(os.path.realpath(filepath)))
	gpx_file = open(filepath, 'r')
	gpx = gpxpy.parse(gpx_file)
	print_info("{} tracks loaded".format(len(gpx.tracks)))
	return gpx


def load_graph(data: geojson.feature.FeatureCollection,
			   attribute_constructor: Callable[[geojson.LineString], Dict]=None,
			   coordinate_convertor: Callable[[float, float], Tuple[float, float]] = None) -> nx.DiGraph:
	g = nx.DiGraph()
	print_info("Creating networkx graph from geojson")
	for item in tqdm(data['features'], desc="processing features"):
		coords = item['geometry']['coordinates']
		if coordinate_convertor:
			coord_from = coordinate_convertor(coords[0][1], coords[0][0])
			coord_to = coordinate_convertor(coords[-1][1], coords[-1][0])
		else:
			coord_from = (coords[0][1], coords[0][0])
			coord_to = (coords[-1][1], coords[-1][0])
		if attribute_constructor:
			g.add_edge(coord_from, coord_to, id=item['properties']['id'], attr=attribute_constructor(item))
		else:
			g.add_edge(coord_from, coord_to, id=item['properties']['id'])
	return g


def load_graph_from_geojson(filepath: str) -> nx.DiGraph:
	data = load_geojson(filepath)
	return load_graph(data)


def load_pickle(filename: str):
	with open(filename, 'rb') as pickled_data:
		data = pickle.load(pickled_data)

	return data

def save_pickle(data, filename):
	with open(filename, 'wb') as f:
		pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)



