"""Creator of geojson from scratch, with any valid geojson. Includes all important data for AgentPolis"""
import argparse
import codecs

import sys

import time

from roadmaptools import utils, clean_geojson, prepare_geojson_to_agentpolisdemo, simplify_graph, calculate_curvature, \
    create_lanes_connections, estimate_speed_from_osm, remove_specific_line_elements, map_elements

__author__ = "Zdenek Bousa"
__email__ = "bousazde@fel.cvut.cz"


def __get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file (.geojson)')
    parser.add_argument('-edges', dest="out_edges", type=str, action='store', help='output file - edges (.geojson)')
    parser.add_argument('-nodes', dest="out_nodes", type=str, action='store', help='output file - nodes (.geojson)')
    return parser.parse_args()


# EXAMPLE OF USAGE
if __name__ == '__main__':
    args = __get_args()
    # input
    input_stream = sys.stdin
    if args.input is not None:
        input_stream = codecs.open(args.input, encoding='utf8')
    # output
    o_edges = codecs.open(args.out_edges, 'w')
    o_nodes = codecs.open(args.out_nodes, 'w')

    start_time = time.time()
    # Load data
    input_geojson = utils.load_geojson(input_stream)

    # Check
    if utils.is_geojson_valid(input_geojson):
        # Prune
        geojson_data = clean_geojson.get_cleaned_geojson(input_geojson)
        # Remove LineString that is not road element in Agentpolis
        geojson_data = remove_specific_line_elements.get_geojson_only_with_elements(geojson_data,
                                                                                    map_elements.get_road_elements_agentpolis())
        # Simplify - (json_dict, simplify edges with same number of lanes?,not simplify edges with different curvature?)
        geojson_data = simplify_graph.get_simplified_geojson(geojson_data, True, False)
        # Estimate speed and length (required properties in graph-importer)
        geojson_data = estimate_speed_from_osm.get_geojson_with_speeds(geojson_data)
        # Calculate curvature
        geojson_data = calculate_curvature.get_geojson_with_curvature(geojson_data)
        # Create lanes connection at each intersection
        connect_lanes = create_lanes_connections
        geojson_data = connect_lanes.get_geojson_with_turn_lanes(geojson_data)
        connect_lanes.print_statistics()
        # Prepare road network/graph for agentpolis
        geojson_data = prepare_geojson_to_agentpolisdemo.get_nodes_and_edges_for_agentpolisdemo(geojson_data)

        # save to file
        utils.save_geojson(geojson_data[0], o_edges)
        utils.save_geojson(geojson_data[1], o_nodes)
    else:
        utils.eprint("Invalid geojson file.")

    print("--- %s seconds ---" % (time.time() - start_time))

    input_stream.close()
    o_nodes.close()
    o_edges.close()
