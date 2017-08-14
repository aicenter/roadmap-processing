import geojson
import codecs
from curvature import Calculation_curvature


class Speed_from_osm:
    def __init__(self, filename):
        self.pathname = filename

    def load_file_and_graph(self):
        print "loading file..."
        with codecs.open(self.pathname, encoding='utf8') as f:
            self.json_dict = geojson.load(f)
        f.close()

    def get_speed(self):
        print "getting speed from map..."
        util = Calculation_curvature('not important here')
        for item in self.json_dict['features']:
            if 'maxspeed' not in item['properties']:
                if item['properties']['highway'] == 'motorway' or item['properties']['highway'] == 'motorway_link': #for czechia
                    item['properties']['speed'] = 130
                else:
                    item['properties']['speed'] = 50
            else:
                item['properties']['speed'] = int(item['properties']['maxspeed'])
            item['properties']['length'] = util.get_length(item['geometry']['coordinates'])

    def save_geojson(self):
        print "saving file..."
        with open("data/speeds-out.geojson", 'w') as outfile:
            geojson.dump(self.json_dict, outfile)
        outfile.close()


if __name__ == '__main__':
    test = Speed_from_osm("data/pruned_file.geojson")
    test.load_file_and_graph()
    test.get_speed()
    test.save_geojson()
