from __future__ import division
import math
import geojson
import codecs
import sys
import argparse


def calculate_curvature(input_stream, output_stream):
    json_dict = load_geojson(input_stream)
    analyse_roads(json_dict)
    save_geojson(json_dict, output_stream)


def get_geojson_with_curvature(json_dict):
    analyse_roads(json_dict)
    return json_dict


def get_node(node):  # latlon
    return (node[1], node[0])


def get_distance_between_coords(point1, point2):  # return in meters
    R = 6371000
    lat1 = math.radians(point1[0])
    lat2 = math.radians(point2[0])
    lat = math.radians(point2[0] - point1[0])
    lon = math.radians(point2[1] - point1[1])

    a = math.sin(lat / 2) * math.sin(lat / 2) + math.cos(lat1) * math.cos(lat2) * math.sin(lon / 2) * math.sin(lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


#        C
#       /\
#    c /  \ a
#     /    \
#   A ----- B
#       b
def calculate_angle_in_degree(a, b, c):
    if a + c > b:  # check if it is a triangle
        angle = math.acos((a ** 2 + c ** 2 - b ** 2) / (2 * a * c))  # in radians
    else:
        angle = 0
    result = abs(180 - math.degrees(angle))
    return result


def get_length(coords):
    length = 0
    for i in range(0, len(coords) - 1):
        point1 = get_node(coords[i])
        point2 = get_node(coords[i + 1])
        length += get_distance_between_coords(point1, point2)
    return length


def get_curvature(coords):
    if len(coords) < 3:
        return [0, 0]  # no curvature on edge
    else:
        total_curvature = 0
        max_curvature = -1
        length_of_edge = 0
        for i in range(0, len(coords) - 2):
            point_a = get_node(coords[i])
            point_b = get_node(coords[i + 1])
            point_c = get_node(coords[i + 2])

            length_c = get_distance_between_coords(point_a, point_b)
            length_a = get_distance_between_coords(point_b, point_c)
            length_b = get_distance_between_coords(point_c, point_a)

            # k = 0.5 * (length_b+length_a+length_c)
            # area = math.sqrt(k*(k-length_a)*(k-length_b)*(k-length_c))
            # radius = (length_b*length_a*length_c)/(4*area)
            angle = calculate_angle_in_degree(length_a, length_b, length_c)
            distance = length_c + length_a
            curvature = angle / distance
            if curvature > max_curvature:
                max_curvature = curvature
            total_curvature += angle
            length_of_edge += distance

        return [total_curvature / length_of_edge, max_curvature]


def load_geojson(in_stream):
    json_dict = geojson.load(in_stream)
    return json_dict


def analyse_roads(json_dict):
    for item in json_dict['features']:
        cur = get_curvature(item['geometry']['coordinates'])
        item['properties']['curvature'] = cur[0]
        item['properties']['max_curvature'] = cur[1]


def save_geojson(json_dict, out_stream):
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

    calculate_curvature(input_stream, output_stream)
    input_stream.close()
    output_stream.close()
