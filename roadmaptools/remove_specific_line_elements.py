"""Remove useless LineStrings"""
import argparse
import codecs

import sys
from roadmaptools import utils, map_elements

__author__ = "Zdenek Bousa"
__email__ = "bousazde@fel.cvut.cz"


def get_geojson_without_elements(json_dict, to_remove_dict):
    return _prune(json_dict, to_remove_dict, False)


def get_geojson_only_with_elements(json_dict, to_keep_dict):
    return _prune(json_dict, to_keep_dict, True)


def _prune(json_dict, elements_dict, boolean_keep):
    for item in json_dict['features']:
        if item['geometry']['type'] == 'LineString':
            try:
                highway = item['properties']['highway']
            except:
                highway = None
            if boolean_keep and highway is not None and highway in elements_dict:
                continue
            elif not boolean_keep and highway not in elements_dict:
                continue
            else:
                item.clear()
    json_dict['features'] = [i for i in json_dict["features"] if i]
    return json_dict


def __get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file (.geojson)')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file (.geojson)')
    return parser.parse_args()


# EXAMPLE OF USAGE
if __name__ == '__main__':
    args = __get_args()
    input_stream = sys.stdin
    output_stream = sys.stdout

    if args.input is not None:
        input_stream = codecs.open(args.input, encoding='utf8')
    if args.output is not None:
        output_stream = codecs.open(args.output, 'w')

    geojson_data = utils.load_geojson(input_stream)
    geojson_data = get_geojson_only_with_elements(geojson_data, map_elements.get_road_elements_agentpolis())
    utils.save_geojson_formatted(geojson_data, output_stream)
    input_stream.close()
    output_stream.close()
