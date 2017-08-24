from __future__ import print_function
from osmread import parse_file, Node, Way
import geojson
from geojson import Point, LineString, Feature, FeatureCollection
import time
from utils import err_print
import argparse

dict_of_coords = dict()


def get_all_coordinates(filename):
    for item in parse_file(filename):  # generator!!
        if isinstance(item, Node):
            dict_of_coords[item.id] = (item.lon, item.lat)


def get_coords_of_edge(nodes):
    loc_coords = []
    for node in nodes:
        try:
            loc_coords.append(dict_of_coords[node])
        except:
            err_print("this node_id {} is required, but not found in OSM!".format(node))
    return loc_coords


def osmtogeojson_converter(filename):
    start_time = time.time()

    get_all_coordinates(filename)

    feature_collection = []

    for item in parse_file(filename):  # generator!!
        if isinstance(item, Node) and item.tags != {}:
            point = Point(dict_of_coords[item.id])
            feature = Feature(geometry=point, id=item.id, properties=item.tags)
            feature_collection.append(feature)
        elif isinstance(item, Way) and 'highway' in item.tags:
            coords = get_coords_of_edge(item.nodes)
            line_string = LineString(coords)
            feature = Feature(geometry=line_string, id=item.id, properties=item.tags)
            feature_collection.append(feature)

    geojson_file = FeatureCollection(feature_collection)

    with open('data/output.geojson', 'w') as outfile:
        geojson.dump(geojson_file, outfile)
    outfile.close()

    validation = geojson.is_valid(geojson_file)
    print("is geoJSON valid?", validation['valid'])

    print("time: {}".format(time.time() - start_time))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('map', type=str, help="map in OSM format")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.2')
    arg = parser.parse_args()

    osmtogeojson_converter(arg.map)
