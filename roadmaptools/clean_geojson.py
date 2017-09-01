import geojson
import codecs
import copy
import argparse
import sys

set_of_useful_properties = {'highway', 'id', 'lanes', 'maxspeed', 'oneway', 'bridge', 'width', 'tunnel', 'traffic_calming', 'lanes:forward', 'lanes:backward'}
dict_of_useful_properties = {'highway': str, 'id': int, 'lanes': int, 'maxspeed': int, 'oneway': str, 'bridge': str, 'width': float, 'tunnel': str, 'traffic_calming': str, 'lanes:forward': int, 'lanes:backward': int}


def clean_geojson(input_stream, output_stream):
    json_dict = load_geojson(input_stream)
    json_deleted = get_geojson_with_deleted_features(json_dict)
    # save_geojson(output_stream, json_deleted)
    prune_geojson_file(json_dict)
    save_geojson(json_dict, output_stream)


def get_cleaned_geojson(json_dict):
    prune_geojson_file(json_dict)
    json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    return json_dict


def remove_properties(item):
    temp_dict_with_props = copy.deepcopy(item['properties'])
    for prop in temp_dict_with_props:
        if prop not in set_of_useful_properties:
            del item['properties'][prop]
    return item


def load_geojson(in_stream):
    json_dict = geojson.load(in_stream)
    return json_dict


def get_geojson_with_deleted_features(json_dict):
    json_deleted = dict()
    json_deleted['type'] = json_dict['type']
    json_deleted['features'] = list()

    for item in json_dict['features']:
        if item['geometry']['type'] != 'LineString':
            json_deleted['features'].append(item)

    # with codecs.open("data/deleted_items.geojson", 'w') as output:
    #     geojson.dump(json_deleted, output)
    # output.close()
    return json_deleted


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
    else:
        new_item['properties']['lanes'] = int(new_item['properties']['lanes'])

    new_item['properties']['oneway'] = 'yes'
    return new_item


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


def prune_geojson_file(json_dict):
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
                        id_iterator += 1
                        continue
                    id_iterator += 1
                    temp = copy.deepcopy(item)
                    new_item = get_single_pair_of_coords(v, u, temp, id_iterator, False)
                    json_dict['features'].append(new_item)

                id_iterator += 1

        item.clear()


def save_geojson(json_dict, out_stream):
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

    clean_geojson(input_stream, output_stream)
    input_stream.close()
    output_stream.close()
