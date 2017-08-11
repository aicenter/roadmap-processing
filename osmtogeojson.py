from osmread import parse_file,Node,Way
import geojson
from geojson import Point,LineString,Feature,FeatureCollection
import time

dict_of_coords = {}

def get_all_coordinates(filename):
    for item in parse_file(filename):  # generator!!
        if isinstance(item, Node):
            dict_of_coords[item.id]=(item.lon,item.lat)

def get_coords_of_edge(nodes):
    loc_coords = []
    for node in nodes:
        loc_coords.append(dict_of_coords[node])
    return loc_coords


def osmtogeojson_converter(filename):
    start_time = time.time()

    get_all_coordinates(filename)

    feature_collection = []

    for item in parse_file(filename):  # generator!!
        if isinstance(item,Node) and item.tags!={}:
            #print item
            point = Point(dict_of_coords[item.id])
            #print point
            feature = Feature(geometry=point,id=item.id,properties=item.tags)
           # print feature
            feature_collection.append(feature)
        elif isinstance(item,Way):
            #print item
            coords = get_coords_of_edge(item.nodes)
            #print coords
            line_string = LineString(coords)
            #print line_string
            feature = Feature(geometry=line_string,id=item.id,properties=item.tags)
            #print feature
            feature_collection.append(feature)

    geojson_file = FeatureCollection(feature_collection)

    with open('data/output.geojson', 'w') as outfile:
        geojson.dump(geojson_file, outfile)
    outfile.close()

    validation = geojson.is_valid(geojson_file)
    print "is geoJSON valid?",validation['valid']

    print "time: {}".format(time.time()-start_time)

if __name__ == '__main__':
    osmtogeojson_converter("data/output.osm")