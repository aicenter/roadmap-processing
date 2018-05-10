import copy

import geojson
from geojson import Point, LineString, Feature, FeatureCollection
from tqdm import tqdm

# properties that will not be deleted
set_of_useful_properties = {'highway', 'id', 'lanes', 'maxspeed', 'oneway', 'bridge', 'width', 'tunnel',
                            'traffic_calming', 'lanes:forward', 'lanes:backward', 'junction'}


def filter_properties(item):
    temp_dict_with_props = copy.deepcopy(item['properties'])
    for prop in temp_dict_with_props:
        if prop not in set_of_useful_properties:
            del item['properties'][prop]
    return item


# for correct type conversion
dict_of_useful_properties = {'highway': str, 'id': int, 'lanes': int, 'maxspeed': int, 'oneway': str, 'bridge': str,
                             'width': float, 'tunnel': str, 'traffic_calming': str, 'lanes:forward': int,
                             'lanes:backward': int, 'junction': str}


def check_property_datatypes(item):
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


def get_single_pair_of_coords(coord_u, coord_v, new_item, id, is_forward):
    new_item['properties']['id'] = id
    del new_item['geometry']['coordinates']
    new_item['geometry']['coordinates'] = [coord_u, coord_v]
    if ('oneway' in new_item['properties'] and new_item['properties']['oneway'] != 'yes') or (
        'oneway' not in new_item['properties']):
        if 'lanes:forward' in new_item['properties'] and is_forward:
            new_item['properties']['lanes'] = int(new_item['properties']['lanes:forward'])
        elif 'lanes:backward' in new_item['properties'] and not is_forward:
            new_item['properties']['lanes'] = int(new_item['properties']['lanes:backward'])
        elif is_forward and 'lanes' in new_item['properties']:
            new_item['properties']['lanes'] = int(new_item['properties']['lanes']) - 1
        elif not is_forward and 'lanes' in new_item['properties']:
            new_item['properties']['lanes'] = 1

    if 'lanes' not in new_item['properties'] or int(new_item['properties']['lanes']) < 1:
        new_item['properties']['lanes'] = 1
    else:
        new_item['properties']['lanes'] = int(new_item['properties']['lanes'])

    new_item['properties']['oneway'] = 'yes'
    return new_item


def make_directed(gj):

    out_features = []
    max_id = max(f['id'] for f in gj['features']) + 1

    for feature in gj['features']:
        if feature['geometry']['type'] == 'LineString':
            out_features.append(feature)
            if 'oneway' not in feature['properties'] or feature['properties']['oneway'] != 'yes':
                # add in segment in opposite direction
                out_features.append(Feature(id=feature['id'] + max_id,
                                            geometry=LineString(list(reversed(feature['geometry']['coordinates']))),
                                            properties=feature['properties']))

    return FeatureCollection(out_features)

def extract_road_network(json_dict):
    """ Extract only the features that constitute road network. """
    id_iterator = 0
    length = len(json_dict['features'])

    for i in tqdm(range(0, length), desc="Pruning geojson", unit_scale=1):
        item = json_dict['features'][i]
        if item['geometry']['type'] == 'LineString':
            item = filter_properties(item)
            check_property_datatypes(item)
            for j in range(0, len(item['geometry']['coordinates']) - 1):
                temp = copy.deepcopy(item)
                u = item['geometry']['coordinates'][j]
                v = item['geometry']['coordinates'][j + 1]
                new_item = get_single_pair_of_coords(u, v, temp, id_iterator, True)
                json_dict['features'].append(new_item)
                if 'oneway' in item['properties']:
                    if item['properties']['oneway'] != 'yes':
                        id_iterator += 1
                        temp = copy.deepcopy(item)
                        new_item = get_single_pair_of_coords(v, u, temp, id_iterator, False)
                        json_dict['features'].append(new_item)
                else:
                    if item['properties']['highway'] == 'motorway' or \
                       item['properties']['highway'] == 'motorway_link' or \
                       item['properties']['highway'] == 'trunk_link'  or \
                       item['properties']['highway'] == 'primary_link' or \
                       ('junction' in item['properties'] and item['properties']['junction'] == 'roundabout'):
                        id_iterator += 1
                        continue
                    id_iterator += 1
                    temp = copy.deepcopy(item)
                    new_item = get_single_pair_of_coords(v, u, temp, id_iterator, False)
                    json_dict['features'].append(new_item)

                id_iterator += 1

        item.clear()


def save_geojson(geojson_dict, output_file):
    """ Validates and saves geojson dictionary to file. """
    result = geojson.is_valid(geojson_dict)
    if not result['valid']:
        print('warning: the resulting geojson is not valid!')

    geojson.dump(geojson_dict, open(output_file, 'w'))
