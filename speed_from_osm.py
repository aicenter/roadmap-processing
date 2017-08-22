from __future__ import print_function
import geojson
import codecs
from curvature import Calculation_curvature
import sys
import argparse

class Speed_from_osm:

    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input', nargs='?', type=str, action='store', help='input file')
        parser.add_argument('output', nargs='?', type=str, action='store', help='output file')
        return parser.parse_args()

    def load_file_and_graph(self,filename=None):
        print("loading file...", file=sys.stderr)
        if filename is not None:
            with codecs.open(filename, encoding='utf8') as f:
                self.json_dict = geojson.load(f)
            f.close()
        else:
            input_filename = self.get_args()
            if input_filename.input is None:
                self.json_dict = geojson.load(sys.stdin)
            else:
                with codecs.open(input_filename.input, encoding='utf8') as f:
                    self.json_dict = geojson.load(f)
                f.close()

    def get_speed(self):
        print("getting speed from map...", file=sys.stderr)
        util = Calculation_curvature()
        for item in self.json_dict['features']:
            if 'maxspeed' not in item['properties']:
                if item['properties']['highway'] == 'motorway' or item['properties']['highway'] == 'motorway_link':  # for czechia
                    item['properties']['speed'] = 130
                else:
                    item['properties']['speed'] = 50
            else:
                item['properties']['speed'] = int(item['properties']['maxspeed'])
            item['properties']['length'] = util.get_length(item['geometry']['coordinates'])

    def save_geojson(self,filename=None):
        print("saving file...", file=sys.stderr)
        if filename is not None:
            with codecs.open(filename, 'w') as out:
                geojson.dump(self.json_dict, out)
            out.close()
        else:
            output_filename = self.get_args()
            if output_filename.output is None:
                geojson.dump(self.json_dict, sys.stdout)
            else:
                with codecs.open(output_filename.output, 'w') as out:
                    geojson.dump(self.json_dict, out)
                out.close()


if __name__ == '__main__':
    test = Speed_from_osm()
    test.load_file_and_graph()
    test.get_speed()
    test.save_geojson()
