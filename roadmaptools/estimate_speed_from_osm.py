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
import geojson
import codecs
from roadmaptools.calculate_curvature import get_length
import sys
import argparse
import time

from geojson import Feature
from roadmaptools.printer import print_info
from roadmaptools.init import config

SPEED_CODE_DICT = {'CZ:urban': 50}


MPH = 1.60934 # miles to km


# https://wiki.openstreetmap.org/wiki/OSM_tags_for_routing/Maxspeed
SPEED_CODE_DICT = {'CZ': {'default':50, 'urban': 50,'living_street':20 ,'pedestrian':20,
                          'motorway':80, 'motorway_link':80,'trunk':80, 'trunk_link':80 },

                   'US': {'default':30*MPH, 'living_street':20*MPH, 'residential':25*MPH, 'primary':45*MPH,
                          'motorway':55*MPH, 'motorway_link':55*MPH,'trunk':5*MPH, 'trunk_link':55*MPH,
                          'secondary':55*MPH, 'tertiary':55*MPH, 'unclassified':55*MPH }}



# length is computed here too!!!
def estimate_posted_speed(input_filename: str, output_filename: str):
    print_info('Estimating travel speed')
    start_time = time.time()

    input_stream = codecs.open(input_filename, encoding='utf8')
    output_stream = open(output_filename, 'w')

    print_info("Loading file from: {}".format(input_filename))
    geojson_file = load_geojson(input_stream)

    print_info("Computing speed")
    geojson_out = get_geojson_with_speeds(geojson_file)

    print_info("Saving file to: {}".format(output_filename))
    save_geojson(geojson_out, output_stream)
    input_stream.close()
    output_stream.close()

    print_info('Speed estimation completed. (%.2f secs)' % (time.time() - start_time))



def estimate_speeds(input_stream, output_stream):
    json_dict = load_geojson(input_stream)
    get_speeds(json_dict)
    save_geojson(json_dict, output_stream)


def get_geojson_with_speeds(json_dict):
    get_speeds(json_dict)
    return json_dict


def load_geojson(in_stream):
    json_dict = geojson.load(in_stream)
    return json_dict


def get_speeds(json_dict):

    for item in json_dict['features']:
        item['properties']['maxspeed'] = get_posted_speed(item)

        item['properties']['length_gps'] = get_length(item['geometry']['coordinates'])
        if item['geometry']['type'].lower() == 'linestring':
            item['properties']['maxspeed'] = get_posted_speed(item)
            item['properties']['length_gps'] = get_length(item['geometry']['coordinates'])


def parse_speed(speed)->float:
    """
    Parses numeric speed data from osm.

    :param speed: List or string. '40', '50 mph', ['20', '30'], ['15 mph', '25 mph']
    :return: float value of maximum allowed speed in km/h
    """

    speed = speed[-1] if isinstance(speed, list) else speed
    if speed.isnumeric():
        return float(speed)


    speed, unit = speed.split(' ')
    if unit.lower() == 'mph':
        return float(speed.split(' ')[0])*MPH
    else:
        return float(speed.split(' ')[0])



def get_country(edge: Feature) -> str:
    """
    Returns code from coordinates.
    (By now only CZ or US based on latitude sign).

    :param edge: geojson feature
    :return: country code
    """

    x,y = edge['geometry']['coordinates'][0]
    if float(x) < 0: return 'US'
    else: return 'CZ'


def get_speed_by_code(country_code:str, speed_tag:str)->float:
    """
    Returns speed value from SPEED_CODE_DICT.
    :param country_code:
    :param speed_tag:
    :return:
    """
    country_codes = SPEED_CODE_DICT[country_code]
    if speed_tag in country_codes.keys():
        return country_codes[speed_tag]
    else:
        return country_codes['default']


def get_posted_speed(edge: Feature) -> float:
    if 'maxspeed' in edge['properties']:
        speed = edge['properties']['maxspeed']

        if(':' in speed):  # country and code, CZ:urban
            country, code = speed.split(':')
            if not country in SPEED_CODE_DICT:
                raise Exception('Country code missing')
            return get_speed_by_code(country, code)
        else:
            return parse_speed(speed)

    # no maxspeed tag in source data
    else:
        country = get_country(edge)
        if not country in SPEED_CODE_DICT:
            raise Exception('Country code missing')

        highway_tag = edge['properties']['highway']
        if highway_tag in SPEED_CODE_DICT[country].keys():
            return  SPEED_CODE_DICT[country][highway_tag]
        else:
            return SPEED_CODE_DICT[country]['default']


def save_geojson(json_dict, out_stream):
    geojson.dump(json_dict, out_stream)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    input_stream = sys.stdin
    output_stream = sys.stdout

    if args.input is not None:
        input_stream = codecs.open(args.input, encoding='utf8')
    if args.output is not None:
        output_stream = codecs.open(args.output, 'w')

    estimate_speeds(input_stream, output_stream)
    input_stream.close()
    output_stream.close()
