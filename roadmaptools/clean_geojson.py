import geojson
import codecs
import copy
import argparse
import sys
from roadmaptools import utils

# Dict of used properties from geojson + id_opposite (tag for twoway)
set_of_useful_properties = {'highway', 'id', 'id_opposite', 'lanes', 'maxspeed', 'oneway', 'bridge', 'width', 'tunnel',
                            'traffic_calming', 'turn:lanes', 'junction'}

dict_of_useful_properties = {'highway': str, 'id': int, 'id_opposite': int, 'lanes': int, 'maxspeed': int,
                             'oneway': str, 'bridge': str,
                             'width': float, 'tunnel': str, 'traffic_calming': str, 'turn:lanes': str, 'junction': str}

DEFAULT_NUMBER_OF_LANES = 1
DEFAULT_TURN = 'all'


#
#   MAIN
#
def clean_geojson(input_stream, output_stream):
    json_dict = utils.load_geojson(input_stream)
    __prune_geojson_file(json_dict)
    utils.save_geojson(json_dict, output_stream)


def get_cleaned_geojson(json_dict):
    __prune_geojson_file(json_dict)
    json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    return json_dict


def get_geojson_with_deleted_features(json_dict):
    json_deleted = dict()
    json_deleted['type'] = json_dict['type']
    json_deleted['features'] = list()

    for item in json_dict['features']:
        if item['geometry']['type'] != 'LineString':
            json_deleted['features'].append(item)
    return json_deleted


#
#   PRIVATE
#
def __prune_geojson_file(json_dict):
    id_iterator = 0
    length = len(json_dict['features'])

    for i in range(0, length):
        item = json_dict['features'][i]
        if item['geometry']['type'] == 'LineString':
            item = __prune_properties(item)
            __check_types(item)
            for c in range(0, len(item['geometry']['coordinates']) - 1):
                temp = copy.deepcopy(item)
                u = item['geometry']['coordinates'][c]
                v = item['geometry']['coordinates'][c + 1]
                new_item = __get_single_pair_of_coords(u, v, temp, id_iterator, True)
                json_dict['features'].append(new_item)
                if 'oneway' in item['properties']:
                    if item['properties']['oneway'] != 'yes':
                        # mark twoway
                        json_dict['features'][(length + id_iterator - 1)]['properties']['id_opposite'] = id_iterator
                        previous_id = json_dict['features'][(length + id_iterator - 1)]['properties']['id']

                        temp = copy.deepcopy(item)
                        # mark two way
                        temp['properties']['id_opposite'] = previous_id

                        # create new two way
                        new_item = __get_single_pair_of_coords(v, u, temp, id_iterator, False)
                        json_dict['features'].append(new_item)
                else:
                    if item['properties']['highway'] == 'motorway' \
                            or item['properties']['highway'] == 'motorway_link' \
                            or item['properties']['highway'] == 'trunk_link' \
                            or item['properties']['highway'] == 'primary_link' \
                            or ('junction' in item['properties'] and item['properties']['junction'] == 'roundabout'):
                        item['properties']['id'] = int(id_iterator)
                        # item['properties']['id_opposite'] = int(-1)
                        # item['properties']['oneway'] = 'yes'
                        id_iterator += 1
                        continue
                    # mark twoway
                    json_dict['features'][(length + id_iterator - 1)]['properties']['id_opposite'] = id_iterator
                    previous_id = json_dict['features'][(length + id_iterator - 1)]['properties']['id']

                    temp = copy.deepcopy(item)
                    # mark two way
                    temp['properties']['id_opposite'] = previous_id

                    new_item = __get_single_pair_of_coords(v, u, temp, id_iterator, False)
                    json_dict['features'].append(new_item)

                id_iterator += 1

        item.clear()


def __prune_properties(item):
    temp_dict_with_props = copy.deepcopy(item['properties'])
    for prop in temp_dict_with_props:
        if prop not in set_of_useful_properties:
            del item['properties'][prop]
    return item


def __get_single_pair_of_coords(coord_u, coord_v, new_item, id, is_forward):
    new_item['properties']['id'] = id  # linear

    # remove and create coordinates in correct order
    del new_item['geometry']['coordinates']
    new_item['geometry']['coordinates'] = [coord_u, coord_v]

    # check number of lanes with oneway
    if ('oneway' in new_item['properties'] and new_item['properties']['oneway'] != 'yes') \
            or ('oneway' not in new_item['properties']):
        if 'lanes:forward' in new_item['properties'] and is_forward:
            new_item['properties']['lanes'] = int(new_item['properties']['lanes:forward'])
        elif 'lanes:backward' in new_item['properties'] and not is_forward:
            new_item['properties']['lanes'] = int(new_item['properties']['lanes:backward'])
        elif is_forward and 'lanes' in new_item['properties']:
            new_item['properties']['lanes'] = int(new_item['properties']['lanes']) - 1
        elif not is_forward and 'lanes' in new_item['properties']:
            new_item['properties']['lanes'] = DEFAULT_NUMBER_OF_LANES
    # default lanes
    if 'lanes' not in new_item['properties'] or new_item['properties']['lanes'] < 1:
        new_item['properties']['lanes'] = DEFAULT_NUMBER_OF_LANES

    # check lanes heading with oneway
    if ('oneway' in new_item['properties'] and new_item['properties']['oneway'] != 'yes') \
            or ('oneway' not in new_item['properties']):
        if 'turn:lanes:forward' in new_item['properties'] and is_forward:
            new_item['properties']['turn:lanes'] = str(new_item['properties']['turn:lanes:forward'])
        elif 'turn:lanes:backward' in new_item['properties'] and not is_forward:
            new_item['properties']['turn:lanes'] = str(new_item['properties']['turn:lanes:backward'])

    # mark oneway
    new_item['properties']['oneway'] = 'yes'

    return new_item


def __check_types(item):
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


def __get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
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

    clean_geojson(input_stream, output_stream)
    input_stream.close()
    output_stream.close()
