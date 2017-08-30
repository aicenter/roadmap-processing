import geojson
import codecs
from geojson import Point, Feature, FeatureCollection
import networkx as nx
import sys
import argparse


def execute_id_maker_and_export_nodes(input_stream, output_stream, formated):
    json_dict = load_geojson(input_stream)
    graph = load_graph(json_dict)
    export_points_to_geojson(graph)
    postprocessing_file(json_dict)
    save_geojson(json_dict, output_stream, formated)


def get_node(node):
    return (node[0], node[1])  # order lonlat


def load_geojson(in_stream):
    json_dict = geojson.load(in_stream)
    return json_dict


def load_graph(json_dict):
    g = nx.MultiDiGraph()
    for item in json_dict['features']:
        coord = item['geometry']['coordinates']
        coord_u = get_node(coord[0])
        coord_v = get_node(coord[-1])
        g.add_edge(coord_u, coord_v, id=item['properties']['id'])
    return g


def export_points_to_geojson(g):
    list_of_features = []
    #for n, _ in g.adjacency_iter():
    for n in g.nodes_iter():
        node_id = get_nodeID(n)
        point = Point(n)
        feature = Feature(geometry=point, properties={'node_id': node_id})
        list_of_features.append(feature)

    json_dict_with_points = FeatureCollection(features=list_of_features)

    with open('data/output-points.geojson', 'w') as outfile:
        geojson.dump(json_dict_with_points, outfile)
    outfile.close()


def get_nodeID(node_id):  # return String
    lon = int(node_id[0] * 10 ** 6)
    lat = int(node_id[1] * 10 ** 6)
    return str(lon) + str(lat)


def postprocessing_file(json_dict):
    for item in json_dict['features']:
        # item['properties']['length'] = item['properties']['distance_best_guess']
        # item['properties']['speed'] = item['properties']['speed_best_guess']
        # del item['properties']['distance_best_guess']
        if 'distance_optimistic' in item['properties']:
            del item['properties']['distance_optimistic']
        if 'distance_pessimistic' in item['properties']:
            del item['properties']['distance_pessimistic']

        from_node = item['geometry']['coordinates'][0]
        to_node = item['geometry']['coordinates'][-1]
        from_nodeID = get_nodeID(from_node)
        to_nodeID = get_nodeID(to_node)
        item['properties']['from_id'] = from_nodeID
        item['properties']['to_id'] = to_nodeID


def save_geojson(json_dict, out_stream, is_formated):
    if is_formated == False:
        geojson.dump(json_dict, out_stream)
    else:
        geojson.dump(json_dict, out_stream, indent=4, sort_keys=True)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file')
    parser.add_argument('-formated', action='store_true', default=False, dest='formated', help='format output file')
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

    execute_id_maker_and_export_nodes(input_stream, output_stream, args.formated)
    input_stream.close()
    output_stream.close()
