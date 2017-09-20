from osmread import parse_file, Node, Way
import geojson
from geojson import Point, LineString, Feature, FeatureCollection
import argparse
import sys
import codecs

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
            # print("this node_id {} is required, but not found in OSM!".format(node),file=sys.stderr)
            pass
    return loc_coords


def convert_osmtogeojson(filename):
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

    # with open('data/output.geojson', 'w') as outfile:
    #     geojson.dump(geojson_file, outfile)
    # outfile.close()
    return geojson_file


def is_geojson_valid(geojson_file):
    validation = geojson.is_valid(geojson_file)
    return validation['valid']


def save_geojson(json_dict, out_stream):
    geojson.dump(json_dict, out_stream)


def get_args():
    parser = argparse.ArgumentParser()
    #    parser.add_argument('map', type=str, help="map in OSM format")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.2')
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    output_stream = sys.stdout

    if args.input is not None:
        input_stream = codecs.open(args.input, encoding='utf8')
    else:
        exit(1)
    if args.output is not None:
        output_stream = codecs.open(args.output, 'w')

    geojson_file = convert_osmtogeojson(args.input)
    save_geojson(geojson_file, output_stream)
