import urllib.request
import os
import bz2
import sys

from tqdm import tqdm
from logging import info
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

#
# with TqdmUpTo(unit='B', unit_scale=True, miniters=1,
# 			  desc=eg_link.split('/')[-1]) as t:  # all optional kwargs
# 	urllib.urlretrieve(eg_link, filename=os.devnull,
# 					   reporthook=t.update_to, data=None)


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
			print_info("\rDecompressing - decompressed size: {:,}B".format(uncompressed_size).replace(",", " "), end='', flush=False)
	uncompressed_size = os.path.getsize(new_filename)
	print_info("\nExtraction finished: uncompressed size: {:,}B".format(uncompressed_size).replace(",", " "))


def get_osm_from_mapzen():
	print_info("Getting map from mapzen.")
	download_file(config.osm_source_url, config.osm_map_filename + ".bz2")
	extract_file(config.osm_map_filename + ".bz2")
	print_info("Map from mapzen ready.")
