from __future__ import division, print_function
import math
import geojson
import codecs
import sys
import argparse


class Calculation_curvature:
    def __init__(self):
        self.json_curvature = {}

    def get_node(self, node):  # latlon
        return (node[1], node[0])

    def get_distance_between_coords(self, point1, point2):  # return in meters
        R = 6371000
        lat1 = math.radians(point1[0])
        lat2 = math.radians(point2[0])
        lat = math.radians(point2[0] - point1[0])
        lon = math.radians(point2[1] - point1[1])

        a = math.sin(lat / 2) * math.sin(lat / 2) + math.cos(lat1) * math.cos(lat2) * math.sin(lon / 2) * math.sin(lon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    #       /\
    #    c /  \ a
    #     /    \
    #     ------
    #       b
    def calculate_angle_in_degree(self, a, b, c):
        if a + c > b:  # check if it is a triangle
            angle = math.acos((a ** 2 + c ** 2 - b ** 2) / (2 * a * c))  # in radians
        else:
            angle = 0
        result = abs(180 - math.degrees(angle))
        return result

    def get_length(self, coords):
        length = 0
        for i in range(0, len(coords) - 1):
            point1 = self.get_node(coords[i])
            point2 = self.get_node(coords[i + 1])
            length += self.get_distance_between_coords(point1, point2)
        return length

    def calculate_curvature(self, coords):
        if len(coords) < 3:
            return [0, 0]  # no curvature on edge
        else:
            total_curvature = 0
            max_curvature = -1
            length_of_edge = 0
            for i in range(0, len(coords) - 2):
                point_a = self.get_node(coords[i])
                point_b = self.get_node(coords[i + 1])
                point_c = self.get_node(coords[i + 2])

                length_c = self.get_distance_between_coords(point_a, point_b)
                length_a = self.get_distance_between_coords(point_b, point_c)
                length_b = self.get_distance_between_coords(point_c, point_a)

                # k = 0.5 * (length_b+length_a+length_c)
                # area = math.sqrt(k*(k-length_a)*(k-length_b)*(k-length_c))
                # radius = (length_b*length_a*length_c)/(4*area)
                angle = self.calculate_angle_in_degree(length_a, length_b, length_c)
                distance = length_c + length_a
                curvature = angle / distance
                if curvature > max_curvature:
                    max_curvature = curvature
                total_curvature += angle
                length_of_edge += distance

            # length_of_edge = self.get_length(coords)
            return [total_curvature / length_of_edge, max_curvature]

    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input',nargs='?', type=str, action='store', help='input file')
        parser.add_argument('output',nargs='?', type=str, action='store', help='output file')
        return parser.parse_args()

    def load_geojson(self,filename=None):
        print("loading file...", file=sys.stderr)
        if filename is not None:
            with codecs.open(filename, encoding='utf8') as f:
                self.json_curvature = geojson.load(f)
            f.close()
        else:
            input_filename = self.get_args()
            if input_filename.input is None:
                self.json_curvature = geojson.load(sys.stdin)
            else:
                with codecs.open(input_filename.input, encoding='utf8') as f:
                    self.json_curvature = geojson.load(f)
                f.close()

    def analyse_roads(self):
        print("processing...", file=sys.stderr)
        for item in self.json_curvature['features']:
            cur = self.calculate_curvature(item['geometry']['coordinates'])
            item['properties']['curvature'] = cur[0]
            item['properties']['max_curvature'] = cur[1]

    def save_geojson(self,filename=None):
        print("saving file...", file=sys.stderr)
        if filename is not None:
            with codecs.open(filename, 'w') as out:
                geojson.dump(self.json_curvature, out)
            out.close()
        else:
            output_filename = self.get_args()
            if output_filename.output is None:
                geojson.dump(self.json_curvature, sys.stdout)
            else:
                with codecs.open(output_filename.output, 'w') as out:
                    geojson.dump(self.json_curvature, out)
                out.close()


# EXAMPLE OF USAGE
if __name__ == '__main__':
    test = Calculation_curvature()
    test.load_geojson()
    test.analyse_roads()
    test.save_geojson()
