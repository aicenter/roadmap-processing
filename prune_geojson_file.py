from __future__ import print_function
import geojson
import codecs
import copy
import logging
import argparse
import sys
from utils import err_print

logger = logging.getLogger('OSM_errors')
set_of_useful_properties = {'highway', 'id', 'lanes', 'maxspeed', 'oneway', 'bridge', 'width', 'tunnel', 'traffic_calming', 'lanes:forward', 'lanes:backward'}
dict_of_useful_properties = {'highway': str, 'id': int, 'lanes': int, 'maxspeed': int, 'oneway': str, 'bridge': str, 'width': float, 'tunnel': str, 'traffic_calming': str, 'lanes:forward': int, 'lanes:backward': int}


def execute(input_stream, output_stream):
    hdlr = logging.FileHandler('data/log.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.WARNING)  # warnings and worse
    json_dict = load_file(input_stream)
    fill_new_geojson_with_deleted_items(json_dict)
    prune_geojson_file(json_dict)
    save_geojson_file(output_stream, json_dict)


def remove_properties(item):
    temp_dict_with_props = copy.deepcopy(item['properties'])
    for prop in temp_dict_with_props:
        if prop not in set_of_useful_properties:
            del item['properties'][prop]
    return item


def load_file(in_stream):
    err_print("loading file...")
    json_dict = geojson.load(in_stream)
    return json_dict


def fill_new_geojson_with_deleted_items(json_dict):
    json_deleted = dict()
    json_deleted['type'] = json_dict['type']
    json_deleted['features'] = list()

    for item in json_dict['features']:
        if item['geometry']['type'] != 'LineString':
            json_deleted['features'].append(item)

    with codecs.open("data/deleted_items.geojson", 'w') as output:
        geojson.dump(json_deleted, output)
    output.close()


def get_single_pair_of_coords(coord_u, coord_v, new_item, id, is_forward):
    new_item['properties']['id'] = id
    del new_item['geometry']['coordinates']
    new_item['geometry']['coordinates'] = [coord_u, coord_v]
    if ('oneway' in new_item['properties'] and new_item['properties']['oneway'] != 'yes') or ('oneway' not in new_item['properties']):
        if 'lanes:forward' in new_item['properties'] and is_forward:
            new_item['properties']['lanes'] = int(new_item['properties']['lanes:forward'])
        elif 'lanes:backward' in new_item['properties'] and not is_forward:
            new_item['properties']['lanes'] = int(new_item['properties']['lanes:backward'])
        elif is_forward and 'lanes' in new_item['properties']:
            new_item['properties']['lanes'] = int(new_item['properties']['lanes']) - 1
        elif not is_forward and 'lanes' in new_item['properties']:
            new_item['properties']['lanes'] = 1

    if 'lanes' not in new_item['properties'] or new_item['properties']['lanes'] < 1:
        new_item['properties']['lanes'] = 1

    new_item['properties']['oneway'] = 'yes'
    return new_item


def write_to_log(value, property, type, id):
    logger.warning('\"%s\" should be %s in %s, id_edge: %d', str(value), type, property, id)


def check_types(item):
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
                    # warnings += "\"{}\" should be integer in {}\n".format(item['properties'][prop],prop)
                    write_to_log(item['properties'][prop], prop, "integer", item['id'])
                    del item['properties'][prop]
            elif dict_of_useful_properties[prop] == str:
                try:
                    str(item['properties'][prop])
                except:
                    # warnings += "\"{}\" should be string in {}\n".format(item['properties'][prop],prop)
                    write_to_log(item['properties'][prop], prop, "string", item['id'])
                    del item['properties'][prop]
            elif dict_of_useful_properties[prop] == int:
                try:
                    int(item['properties'][prop])
                except:
                    # warnings += "\"{}\" should be long in {}\n".format(item['properties'][prop],prop)
                    write_to_log(item['properties'][prop], prop, "long", item['id'])
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
                    # warnings += "\"{}\" should be float in {}\n".format(item['properties'][prop],prop)
                    write_to_log(item['properties'][prop], prop, "float", item['id'])
                    del item['properties'][prop]


def prune_geojson_file(json_dict):
    err_print("processing...")
    id_iterator = 0
    length = len(json_dict['features'])

    for i in range(0, length):
        item = json_dict['features'][i]
        if item['geometry']['type'] == 'LineString':
            item = remove_properties(item)
            check_types(item)
            for i in range(0, len(item['geometry']['coordinates']) - 1):
                temp = copy.deepcopy(item)
                u = item['geometry']['coordinates'][i]
                v = item['geometry']['coordinates'][i + 1]
                new_item = get_single_pair_of_coords(u, v, temp, id_iterator, True)
                json_dict['features'].append(new_item)
                if 'oneway' in item['properties']:
                    if item['properties']['oneway'] != 'yes':
                        id_iterator += 1
                        temp = copy.deepcopy(item)
                        new_item = get_single_pair_of_coords(v, u, temp, id_iterator, False)
                        json_dict['features'].append(new_item)
                else:
                    if item['properties']['highway'] == 'motorway' or item['properties']['highway'] == 'motorway_link' or item['properties']['highway'] == 'trunk_link' \
                            or item['properties']['highway'] == 'primary_link' or ('junction' in item['properties'] and item['properties']['junction'] == 'roundabout'):
                        continue
                    id_iterator += 1
                    temp = copy.deepcopy(item)
                    new_item = get_single_pair_of_coords(v, u, temp, id_iterator, False)
                    json_dict['features'].append(new_item)

                id_iterator += 1

        item.clear()


def save_geojson_file(out_stream, json_dict):
    err_print("saving file...")
    json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    geojson.dump(json_dict, out_stream)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
    return parser.parse_args()


# EXAMPLE OF USAGE
if __name__ == '__main__':
    args = get_args()
    input_stream = sys.stdin
    output_stream = sys.stdout

    if args.input is not None:
        input_stream = codecs.open(args.input, encoding='utf8')
    if args.output is not None:
        output_stream = codecs.open(args.output, 'w')

    execute(input_stream, output_stream)
    input_stream.close()
    output_stream.close()
