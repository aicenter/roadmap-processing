"""Finds connecting edges (ids) for specified turn lanes.

Prune data:
    1. By road_elements (try to connect only them)
    2. By degree of node, prune only with degree > 2
    - on remaining elements the algorithm will try to calcu

Error check:
    1. Checks for correct number of lanes and eventually updates them.

Data output:
    list_of_lanes = (Lane1(dict_direction1:following_edge_id,dict_direction2:following_edge_id),
    Lane2(dict_direction1:following_edge_id))

    For unknown situation list_of_lanes might be None or following_edge_id = -1 or dict_directionX.key = 'none'.
    This is with respect to osm wiki.

"""
import argparse
import codecs

import networkx as nx
import sys

from roadmaptools import coords, utils, map_elements
from math import degrees
from copy import deepcopy

__author__ = "Zdenek Bousa"
__email__ = "bousazde@fel.cvut.cz"

road_elements = map_elements.get_road_elements_agentpolis()  # Road elements available for lanes direction

road_directions = {'sharp_left', 'left', 'slight_left', 'through', 'slight_right', 'right', 'sharp_right',
                   'none'}  # junction
road_directions_extra = {'reverse', 'merge_to_left', 'merge_to_right'}  # ignore these tags

# Variables
tag_turn = 'turn:lanes'
tag_id = 'id'
tag_junction = 'junction'
tag_highway = 'highway'
tag_roundabout = 'roundabout'
extend_logging = False

# Internal variables
number_of_inconsistent_edges = 0


#
# PUBLIC
#
def get_geojson_with_turn_lanes(json_dict):
    """Return json dict without logging on error output"""
    return process(json_dict)


def process(json_dict, logging=False):
    """Main function, returns json dict.
     It is better to run this after simplification"""
    global extend_logging
    extend_logging = logging
    graph = __load_graph(json_dict)
    data = __traverse_graph_and_connect(graph)
    return ToJson.graph_to_json(data, json_dict)


def get_number_of_inconsistent_edges():
    return number_of_inconsistent_edges


def __load_graph(json_dict):
    """Load graph from json dict with id,lanes,turn:lanes + all data

    Prune data:
    1. By road_elements (try to connect only them)
    2. By degree of node, prune only with degree > 2
    """
    g = nx.MultiDiGraph()
    for item in json_dict['features']:
        coord = item['geometry']['coordinates']
        coord_u = coords.get_lat_lon(coord[0])
        coord_v = coords.get_lat_lon(coord[-1])
        if coord_u != coord_v or len(coord) != 2:  # prune loops without any purpose, save loops like traffic roundabout
            lanes = item['properties']['lanes']
            lanes_turn = ItemProperties.get_turn_lanes(item)
            junction = ItemProperties.get_junction(item)
            highway = ItemProperties.get_highway(item)
            if highway in road_elements:  # prune non-road elements
                g.add_edge(coord_u, coord_v, id=item['properties'][tag_id], lanes=lanes, lanes_turn=lanes_turn,
                           junction=junction, highway=highway)

    return g


def __traverse_graph_and_connect(graph):
    """Traverse graph and add agentpolis:turn:id to road elements (ID of following edge, that is available at
    intersection).

    To unknown direction add all possible directions

    Prune data:
    1. By road_elements (try to connect only them)
    2. By degree of node, prune only with degree > 2

    Return list of modified edges
    """
    # create dictionary with junction node (from node) as a key + coords,junction,turn_lanes
    dict_out_edges = dict()
    for e in graph.out_edges(data=True):
        key = __get_hash(e[0])
        if key not in dict_out_edges:
            dict_out_edges[key] = list()
        dict_out_edges[key].append(
            (e[0], e[1], e[2]['id'], e[2]['junction'], e[2]['highway']))  # coord A, coord B, id, junction, highway

    # create dictionary with junction node (to node) as a key + coords,junction,turn_lanes
    dict_in_edges = dict()
    for e in graph.in_edges(data=True):
        key = __get_hash(e[1])
        if key not in dict_in_edges:
            dict_in_edges[key] = list()
        dict_in_edges[key].append(
            (e[0], e[1], e[2]['lanes_turn'], e[2]['lanes'],
             e[2]['junction'], e[2]['id'], e[2]['highway']))  # coord A, coord B, lanes, #lanes, junction,id, highway

    modified_edges = list()
    # Get junctions
    for node in graph.nodes():
        degree = graph.degree(node)
        # prune nodes by degree
        if degree > 2:  # it has to be junction
            # calculate angles at intersection and fill modified edges
            try:
                __calculate_junction(dict_in_edges[__get_hash(node)], dict_out_edges[__get_hash(node)], modified_edges)
            except KeyError as e:
                if extend_logging:
                    utils.eprint("Error: Incorrect node or is not part of road element", str(e), "junction skipped.")
                else:
                    pass
    return modified_edges


def __calculate_junction(list_in_edges, list_out_edges, modified_edges):
    """"""
    global number_of_inconsistent_edges
    for in_e in list_in_edges:
        if in_e[2] is None:  # no turn lanes available for this in_edge
            continue  # continue to next incoming edge to the node
        else:  # turn lanes available
            in_e = deepcopy(in_e)
            list_out_edges = deepcopy(list_out_edges)
            # Incoming edge
            e_coords1 = in_e[0]
            e_coords2 = in_e[1]
            e_turn_lanes = in_e[2]
            e_number_of_lanes = in_e[3]
            e_junction = in_e[4]
            e_id = in_e[5]
            e_highway = in_e[6]

            # parse turn lanes
            list_of_directions, turns_data_parsed = __parse_turn_lanes(e_turn_lanes)

            # check data consistency
            if len(turns_data_parsed) != e_number_of_lanes:
                # update number of lanes
                e_number_of_lanes = len(turns_data_parsed)
                number_of_inconsistent_edges += 1
                if extend_logging:
                    utils.eprint("Inconsistent data in edge: " + str(e_id))
            through_id = -1
            roundabout = False
            # If it is roundabout, then try to connect through direction to the rest of the roundabout
            if e_junction == tag_roundabout:
                # get out edge and following roundabout
                for out_e in list_out_edges:
                    if out_e[3] == tag_roundabout:
                        through_id = out_e[2]
                        list_out_edges.remove(out_e)
                        try:
                            list_of_directions.remove('through')
                        except ValueError:
                            list_of_directions.remove('slight_left')
                        roundabout = True
                        break

            # calculate rest of directions
            dict_data = __calculate_directions(in_e, list_out_edges, roundabout)
            if through_id != -1:
                dict_data['through'] = through_id  # append data about roundabout

            dict_turns_data_with_id = __rebuild_according_to_lanes(turns_data_parsed, dict_data)

            # Create modified edge
            modified_edge = (
                e_coords1, e_coords2, e_turn_lanes, e_number_of_lanes, e_junction, e_id, e_highway,
                dict_turns_data_with_id)

            # Append to changelist
            modified_edges.append(modified_edge)
    return modified_edges


def __rebuild_according_to_lanes(dict_turns_data_parsed, dict_directions):
    """Fill data from dict_directions to dict_turns_data_parsed"""
    for lane in dict_turns_data_parsed:
        for direction in lane.keys():
            if direction is not None:
                lane[direction] = -1
                # try default from dict
                lane[direction] = __try_direction(direction, dict_directions)
                if lane[direction] != -1:
                    continue

                #switch left/right
                switch = None
                if "right" in str(direction):
                    switch = "right"
                elif "left" in str(direction):
                    switch = "left"

                if switch is not None:
                    # Normal turn
                    if direction == str(switch):
                        lane[direction] = __try_direction("slight_"+str(switch), dict_directions)
                        if lane[direction] != -1:
                            continue
                    if direction == str(switch):
                        lane[direction] = __try_direction("sharp_"+str(switch), dict_directions)
                        if lane[direction] != -1:
                            continue
                    # Slight
                    if direction == ("slight_"+str(switch)):
                        lane[direction] = __try_direction(str(switch), dict_directions)
                        if lane[direction] != -1:
                            continue
                    # Sharp
                    if direction == ("sharp_"+str(switch)):
                        lane[direction] = __try_direction(str(switch), dict_directions)
                        if lane[direction] != -1:
                            continue

                # Exception
                if extend_logging:
                    utils.eprint("Error: No match for equested direction with computed")
            else:
                lane[direction] = -1

    return dict_turns_data_parsed


def __try_direction(direction, dict_directions):
    try:
        return dict_directions[direction]
    except KeyError:
        return -1


def __calculate_directions(in_edge, out_edges, roundabout):
    """Assign for each direction an ID
    Return dict(direction:id)
    """
    dict_angle = dict()
    dict_directions_id = dict()
    # Find angles of all outgoing edges
    for e in out_edges:
        a = __get_angle_between_edges(in_edge, e)
        id = e[2]
        dict_angle[a] = id

    # sort angles from -180 to 180
    list_angles = dict_angle.keys()
    list_angles.sort()

    # convert angles to directions
    for a in list_angles:
        # Straight and reverse
        if ((-160 >= a >= -180) or (180 >= a >= 160)) and not roundabout:  # through
            dict_directions_id['through'] = dict_angle[a]
        elif -20 <= a <= 20:  # turn back
            dict_directions_id['reverse'] = dict_angle[a]
        # Roundabout
        elif roundabout and (-180 <= a <= -20):  # roundabout exit right
            dict_directions_id['right'] = dict_angle[a]
        elif roundabout and (180 >= a >= 20):  # roundabout exit left
            dict_directions_id['left'] = dict_angle[a]
        # Right
        elif -160 < a < -140:  # slight right
            dict_directions_id['slight_right'] = dict_angle[a]
        elif -40 < a < -20:  # sharp right
            dict_directions_id['sharp_right'] = dict_angle[a]
        elif -140 <= a <= -40:  # right
            dict_directions_id['right'] = dict_angle[a]
        # Left
        elif 160 > a > 140:  # slight left
            dict_directions_id['slight_left'] = dict_angle[a]
        elif 40 > a > 20:  # sharp left
            dict_directions_id['sharp_left'] = dict_angle[a]
        elif 140 >= a >= 40:  # left
            dict_directions_id['left'] = dict_angle[a]
        else:
            utils.eprint("Error, unknown orientation for angle(degrees): " + a)

    return dict_directions_id


def __parse_turn_lanes(data):
    """ Return list of dictionaries. List of lanes that will be available"""
    list_of_directions = list()
    list_of_lanes_directions = list()
    lanes = data.split("|")  # split by lanes
    for l in lanes:  # for each lane separated by |, e.g. right;right|sharp_right
        dir_dict = dict()
        directions = l.split(";")
        for direction in directions:  # for each direction, e.g. right;right
            if direction == "":
                dir_dict['none'] = -1
            elif direction in road_directions:
                dir_dict[direction] = -1  # correct ids will be assigned later
                # add to list of directions
                if direction not in list_of_directions:
                    list_of_directions.append(direction)
            else:
                pass  # ignore this data
        if len(dir_dict) > 0:
            list_of_lanes_directions.append(dir_dict)
    return list_of_directions, list_of_lanes_directions


def __get_hash(coordinates):
    """Return string from coordinates"""
    return str(str(coordinates[0]) + "-" + str(coordinates[1]))


def __get_angle_between_edges(in_edge, out_edge):
    """Get angle between incoming_edge and outgoing_edge.
    Note: in_edge[1] = out_edge[0]
    """
    p_a = coords.get_coordinates_in_radians(coords.get_lat_lon(in_edge[0]))
    p_b = coords.get_coordinates_in_radians(coords.get_lat_lon(in_edge[1]))
    p_c = coords.get_coordinates_in_radians(coords.get_lat_lon(out_edge[1]))

    angle = degrees(coords.angle_between_points(p_a, p_b, p_b, p_c))
    if not (-180 <= angle <= 180):
        ValueError("Out of interval")
    return angle


class ItemProperties:
    """ Getters for LineString/Point properties."""

    def __init__(self):
        pass

    @staticmethod
    def get_turn_lanes(item):
        """Parse turn:lanes from item properties.
        Return: string/none
        """
        turn_lanes = None
        try:
            turn_lanes = item['properties'][tag_turn]
        except:
            if extend_logging:
                utils.eprint("No turn lanes available for object " + str(item['properties'][tag_id]))
        return turn_lanes

    @staticmethod
    def get_junction(item):
        """Parse junction from item properties.
        Return: string/none"""
        junction = None
        try:
            junction = item['properties'][tag_junction]
        except:
            if extend_logging:
                utils.eprint("No junction available for object " + str(item['properties'][tag_id]))
        return junction

    @staticmethod
    def get_highway(item):
        """Parse highway from item properties.
            Return: string/none"""
        type = None
        try:
            type = item['properties'][tag_highway]
        except:
            if extend_logging:
                utils.eprint("No junction available for object " + str(item['properties'][tag_id]))
        return type


class ToJson:
    # Prepare json dict from graph
    def __init__(self):
        pass

    @staticmethod
    def graph_to_json(modified_edges, json_dict):
        """Prepare json dict from graph"""
        dict_of_edges = dict()
        for e in modified_edges:
            dict_of_edges[e[5]] = modified_edges.index(e)  # Hash structure for searching id and match with rest of data

        for item in json_dict['features']:
            i = item['properties']['id']
            if i in dict_of_edges.keys():
                edge = modified_edges[dict_of_edges[i]]
                properties = item['properties']

                # e_coords1, e_coords2, e_turn_lanes, e_number_of_lanes, e_junction, e_id, e_highway, dict_turns_data_with_id)
                properties['lanes'] = edge[3]
                properties['turn:lanes:id'] = edge[7]

        json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts

        return json_dict


def __get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.2')
    parser.add_argument('-i', dest="input", type=str, action='store', help='input file (.geojson)')
    parser.add_argument('-o', dest="output", type=str, action='store', help='output file (.geojson)')
    parser.add_argument('-log', action='store_true', default=False, dest='log', help='Turn log on stderr.')
    return parser.parse_args()


# EXAMPLE OF USAGE
if __name__ == '__main__':
    args = __get_args()
    output_stream = sys.stdout
    input_stream = sys.stdin

    if args.output is not None:
        output_stream = codecs.open(args.output, 'w')
    if args.input is not None:
        input_stream = codecs.open(args.input, 'r')

    geojson_file = utils.load_geojson(input_stream)
    if utils.is_geojson_valid(geojson_file):
        geojson_file = process(geojson_file, args.log)
        utils.save_geojson(geojson_file, output_stream)
    else:
        utils.eprint("Invalid geojson file")

    input_stream.close()
    output_stream.close()
