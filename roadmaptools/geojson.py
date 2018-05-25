import copy

import geojson
from geojson import Point, LineString, Feature, FeatureCollection
from tqdm import tqdm
import shapely.geometry

# properties that will not be deleted
set_of_useful_properties = {'highway', 'id', 'lanes', 'maxspeed', 'oneway', 'bridge', 'width', 'tunnel',
                            'traffic_calming', 'lanes:forward', 'lanes:backward', 'junction'}


# for correct type conversion
property_data_types = {'highway': str, 'id': int, 'lanes': int, 'maxspeed': int, 'oneway': str, 'bridge': str,
                             'width': float, 'tunnel': str, 'traffic_calming': str, 'lanes:forward': int,
                             'lanes:backward': int, 'junction': str}



def sanitize_feature_properties(in_feature):
    feature = copy.deepcopy(in_feature)
    for prop in property_data_types:
        if prop in feature['properties'] and not isinstance(feature['properties'][prop], property_data_types[prop]):
            if property_data_types[prop] == int:
                try:
                    if " mph" in feature['properties'][prop]:
                        temp = feature['properties'][prop].split()
                        feature['properties'][prop] = float(temp[0]) * 1.609344
                    elif " knots" in feature['properties'][prop]:
                        temp = feature['properties'][prop].split()
                        feature['properties'][prop] = float(temp[0]) * 1.85200
                    else:
                        int(feature['properties'][prop])
                except:
                    del feature['properties'][prop]
            elif property_data_types[prop] == str:
                try:
                    str(feature['properties'][prop])
                except:
                    del feature['properties'][prop]
            elif property_data_types[prop] == int:
                try:
                    int(feature['properties'][prop])
                except:
                    del feature['properties'][prop]
            elif property_data_types[prop] == float:
                try:
                    if " m" in feature['properties'][prop]:
                        temp = feature['properties'][prop].split()
                        feature['properties'][prop] = float(temp[0])
                    elif " km" in feature['properties'][prop]:
                        temp = feature['properties'][prop].split()
                        feature['properties'][prop] = float(temp[0]) * 1000
                    elif " mi" in feature['properties'][prop]:
                        temp = feature['properties'][prop].split()
                        feature['properties'][prop] = float(temp[0]) * 1609.344
                    else:
                        float(feature['properties'][prop])
                except:
                    del feature['properties'][prop]

    return feature



def get_subsegement(feature: dict, j: int,  id: int, is_forward: bool):
    """
    Returns LineString feature that represents j-th segment of given complex LineString feature.

    Parameters
    ----------
    feature:
        input feature
    j:
        the number of the segment to be extracted
    id:
        the id of the newly constructed feature
    is_forward
        true: return forward directed segment,
        false: return backward directed segment

    Returns
    -------
        dict representing the new feature

    """

    out_feature = copy.deepcopy(feature)

    out_feature['properties']['id'] = id

    u = feature['geometry']['coordinates'][j]
    v = feature['geometry']['coordinates'][j + 1]
    if is_forward:
        out_feature['geometry']['coordinates'] = [u, v]
    else:
        out_feature['geometry']['coordinates'] = [v, u]

    if ('oneway' in feature['properties'] and feature['properties']['oneway'] != 'yes') \
            or ('oneway' not in feature['properties']):
        if 'lanes:forward' in feature['properties'] and is_forward:
            out_feature['properties']['lanes'] = int(feature['properties']['lanes:forward'])
        elif 'lanes:backward' in feature['properties'] and not is_forward:
            out_feature['properties']['lanes'] = int(feature['properties']['lanes:backward'])
        elif is_forward and 'lanes' in feature['properties']:
            out_feature['properties']['lanes'] = int(feature['properties']['lanes']) - 1
        elif not is_forward and 'lanes' in feature['properties']:
            out_feature['properties']['lanes'] = 1

    if 'lanes' not in feature['properties'] or int(feature['properties']['lanes']) < 1:
        out_feature['properties']['lanes'] = 1
    else:
        out_feature['properties']['lanes'] = int(feature['properties']['lanes'])

    out_feature['properties']['oneway'] = 'yes'

    return out_feature


def simplify_features(input_gj, tolerance: float):
    """
    Returns a simplified geometry produced by the Douglas-Peucker algorithm


    Simplifies each LineString feature using
    Parameters
    ----------
    input_gj: dict
        input geojson

    tolerance: float
        coordinates of the simplified geometry will be no more than the
        tolerance distance from the original.


    Returns
    -------
    Geojson where all LineString features are simplified.

    """
    out_features = []

    for feature in input_gj['features']:
        if feature['geometry']['type'] == 'LineString':

            sls = shapely.geometry.LineString(feature['geometry']['coordinates'])
            sls2 = sls.simplify(tolerance)

            out_features.append(Feature(id=feature['id'],
                                            geometry=LineString(list(sls2.coords)),
                                            properties=feature['properties']))
    return FeatureCollection(out_features)


def make_directed(input_gj):
    """
    Converts features that represent two-way roads into two features, each representing one direction.

    Parameters
    ----------
    input_gj: dict
        input geojson with features

    Returns
    -------
       dict: geojson with 'directed' edges

    """
    out_features = []
    max_id = max(f['id'] for f in input_gj['features']) + 1

    for feature in input_gj['features']:
        if feature['geometry']['type'] == 'LineString':
            out_features.append(feature)
            if 'oneway' not in feature['properties'] or feature['properties']['oneway'] != 'yes':
                simplified_geometry = feature['geometry']
                # add in segment in opposite direction
                out_features.append(Feature(id=feature['id'],
                                            geometry=simplified_geometry,
                                            properties=feature['properties']))

    return FeatureCollection(out_features)

def sanitize_geojson_properties(input_geojson):
    """
    Performs basic sanitization of properties of features in the given geojson.

    Parameters
    ----------
    input_geojson

    Returns
    -------
        sanitized geojson

    """
    out_features = []

    for feature in input_geojson['features']:
        out_features.append(sanitize_feature_properties(feature))

    return FeatureCollection(out_features)


def extract_road_network(json_dict):
    """
    Extracts road network from given geojson features.
    In particular:
        * Complex LineString geometries are broken to sequence of atomic line geometries.
        * For every two-way road, two on-way lines are generated.


    Parameters
    ----------
    json_dict: input dict

    Returns
    -------
    geojson with LineString features representing atomic line segements

    """

    out_features = []

    new_feature_id = 0
    length = len(json_dict['features'])

    for i in tqdm(range(0, length), desc="Extracting roadmap", unit_scale=1):
        feature = json_dict['features'][i]
        if feature['geometry']['type'] == 'LineString':
            # feature = filter_properties(feature)
            for j in range(0, len(feature['geometry']['coordinates']) - 1):

                is_one_way = ('oneway' in feature['properties'] and feature['properties']['oneway'] == 'yes') \
                    or feature['properties']['highway'] == 'motorway' \
                    or feature['properties']['highway'] == 'motorway_link' \
                    or feature['properties']['highway'] == 'trunk_link' \
                    or feature['properties']['highway'] == 'primary_link' \
                    or ('junction' in feature['properties'] and feature['properties']['junction'] == 'roundabout')


                out_features.append(get_subsegement(feature, j, new_feature_id, True))
                if not is_one_way:
                    out_features.append(get_subsegement(feature, j, new_feature_id, False))

                new_feature_id += 1

    return FeatureCollection(out_features)


def save_geojson(geojson_dict, output_file):
    """ Validates and saves geojson dictionary to file. """
    result = geojson.is_valid(geojson_dict)
    if not result['valid']:
        print('warning: the resulting geojson is not valid!')

    geojson.dump(geojson_dict, open(output_file, 'w'))
