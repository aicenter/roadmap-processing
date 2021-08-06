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
from typing import Tuple
import geojson
import codecs
from roadmaptools.calculate_curvature import get_length
import sys
import argparse
import time

from geojson import Feature
from roadmaptools.printer import print_info
from roadmaptools.init import config

MPH = 1.60934  # miles to km

# https://wiki.openstreetmap.org/wiki/OSM_tags_for_routing/Maxspeed
SPEED_CODE_DICT = {'CZ': {'default': 50, 'urban': 50, 'living_street': 20, 'pedestrian': 20,
                          'motorway': 80, 'motorway_link': 80, 'trunk': 80, 'trunk_link': 80},

                   'US': {'default': 30, 'living_street': 20, 'residential': 25, 'primary': 45,
                          'motorway': 55, 'motorway_link': 55, 'trunk': 5, 'trunk_link': 55,
                          'secondary': 55, 'tertiary': 55, 'unclassified': 55}}

DEFAULT_UNIT = "kmh"
UNIT_MAP = {'US': "mph", "CZ": "kmh"}

TO_METERS_PER_SECOND = {"kmh": 3.6, "mph": 2.2369362920544}


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


def parse_speed(speed) -> Tuple[int, str]:
    """
    Parses numeric speed data from osm.

    :param speed: List or string. '40', '50 mph', ['20', '30'], ['15 mph', '25 mph']
    :return: float value of maximum allowed speed in km/h
    """

    speed = speed[-1] if isinstance(speed, list) else speed
    if speed.isnumeric():
        return int(speed), DEFAULT_UNIT

    speed, unit = speed.split(' ')
    unit_lower = unit.lower()
    if unit_lower == 'mph':
        return int(speed.split(' ')[0]), unit_lower
    else:
        raise Exception("Unsupported unit: {}".format(unit))
        # return float(speed.split(' ')[0])


def get_country(edge: Feature) -> str:
    """
    Returns code from coordinates.
    (By now only CZ or US based on latitude sign).

    :param edge: geojson feature
    :return: country code
    """

    x, y = edge['geometry']['coordinates'][0]
    if float(x) < 0:
        return 'US'
    else:
        return 'CZ'


def get_speed_by_code(country_code: str, speed_tag: str) -> int:
    """
    Returns speed value from SPEED_CODE_DICT.
    :param country_code:
    :param speed_tag:
    :return:
    """
    speeds_for_country = SPEED_CODE_DICT[country_code]
    if speed_tag in speeds_for_country.keys():
        return speeds_for_country[speed_tag]
    else:
        return speeds_for_country['default']


def get_posted_speed(edge: Feature) -> Tuple[int, str]:
    if 'maxspeed' in edge['properties']:
        speed = edge['properties']['maxspeed']

        if ':' in speed:
            #  Parse speed from OSM speed code, e.g. CZ:urban
            country_code, code = speed.split(':')
            if country_code not in SPEED_CODE_DICT:
                raise Exception('Country code missing')
            return get_speed_by_code(country_code, code), UNIT_MAP[country_code]
        else:
            # Parse speed from speed string, e.g. `40` or `25 mph`
            return parse_speed(speed)

    # no maxspeed tag in source data, we use the highway tag to deetermine the max speed
    else:
        country_code = get_country(edge)
        if country_code not in SPEED_CODE_DICT:
            raise Exception('Country code missing')

        highway_tag = edge['properties']['highway']
        if highway_tag in SPEED_CODE_DICT[country_code].keys():
            return SPEED_CODE_DICT[country_code][highway_tag], UNIT_MAP[country_code]
        else:
            return SPEED_CODE_DICT[country_code]['default'], UNIT_MAP[country_code]


def save_geojson(json_dict, out_stream):
    geojson.dump(json_dict, out_stream)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
    return parser.parse_args()


def get_speed_per_second_from_edge(edge: dict, scale: float=1, use_measured_speed: bool=False) -> float:
    speed = edge['properties']['measured_speed'] if use_measured_speed else edge['properties']['maxspeed']
    unit = edge['properties']['speed_unit']
    return get_speed_per_second(speed, unit, scale)


def get_speed_per_second(speed: int, unit: str, scale: float = 1) -> float:
    return speed * scale / TO_METERS_PER_SECOND[unit]


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
