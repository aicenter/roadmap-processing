"""Example on how to create geojson from osm."""
import argparse
import codecs

import sys
from roadmaptools import utils, osmtogeojson


def __get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.2')
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file (.osm)')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file (.geojson)')
    return parser.parse_args()


# EXAMPLE OF USAGE
if __name__ == '__main__':
    args = __get_args()
    output_stream = sys.stdout

    if args.output is not None:
        output_stream = codecs.open(args.output, 'w')

    geojson_file = osmtogeojson.convert_osmtogeojson(args.input)
    utils.save_geojson(geojson_file, output_stream)

    output_stream.close()
