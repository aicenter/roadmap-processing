import time
import platform
import os
import subprocess

from roadmaptools.printer import print_info, print_err
from roadmaptools.init import config


def filter_osm_file():
	""" Downloads (and compiles) osmfilter tool from web and
	calls that osmfilter to only filter out only the road elements.
	"""

	print_info('Filtering OSM file...')
	start_time = time.time()

	if check_osmfilter():
		params = '--keep="highway=motorway =motorway_link =trunk =trunk_link =primary =primary_link =secondary' \
				 ' =secondary_link =tertiary =tertiary_link =unclassified =unclassified_link =residential =residential_link' \
				 ' =living_street" --drop="access=no"'

		command = './osmfilter' if platform.system() == 'Linux' else 'osmfilter.exe'

		filter_command = '%s %s %s > %s' % (command, config.osm_map_filename, params, config.filtered_osm_filename)
		os.system(filter_command)
	else:
		print_info('Osmfilter not available. Exiting.')
		exit(1)

	print_info('Filtering finished. (%.2f secs)' % (time.time() - start_time))


def check_osmfilter():
	# determine if osmfilter is installed, otherwise download it

	print_info("Checking if osmfilter is installed.")

	my_platform = platform.system()  # get system info. Values: 'Linux', 'Windows'
	if my_platform == 'Linux':  # check if osmfilter is downloaded
		executable = 'osmfilter'

		if not os.path.exists(executable):
			print_info('Downloading and compiling osmfilter... ')
			os.system('wget -O - http://m.m.i24.cc/osmfilter.c |cc -x c - -O3 -o osmfilter')

		return True

	elif my_platform == 'Windows':
		executable = 'osmfilter.exe'

		if not os.path.exists(executable):
			print_info('Downloading and compiling osmfilter... ')
			try:
				subprocess.call(['wget', 'http://m.m.i24.cc/osmfilter.exe', '--no-check-certificate'])
			except OSError as e:
				if e.errno == os.errno.ENOENT:
					print_err('wget not found! Please, install it.')  # handle file not found error
				else:
					raise  # something else went wrong while trying to run `wget`

				return False
		return True

	else:
		print_err('OSM filtering not implemented for platform: %s. ' % my_platform)
		return False
