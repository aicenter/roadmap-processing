import urllib.request
import shutil
import os
import bz2

from roadmaptools.init import config


def download_file(url: str, file_name: str):
	with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
		shutil.copyfileobj(response, out_file)


def extract_file(filename: str):
	new_filename = filename.replace(".bz2", "")
	with open(new_filename, 'wb') as new_file, bz2.BZ2File(filename, 'rb') as file:
		for data in iter(lambda: file.read(100 * 1024), b''):
			new_file.write(data)


def get_osm_from_mapzen():
	download_file(config.osm_source_url, config.osm_map_filename + ".bz2")
	extract_file(config.osm_map_filename + ".bz2")