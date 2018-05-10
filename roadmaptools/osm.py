import geojson
import osmread
from geojson import Point, LineString, Feature, FeatureCollection

from roadmaptools.util import filter_dict


DEFAULT_KEEP_TAGS = {'highway', 'id', 'lanes', 'maxspeed', 'oneway', 'bridge', 'width', 'tunnel',
                'traffic_calming', 'lanes:forward', 'lanes:backward', 'junction'}

def osm_to_geojson(filename, keep_tags='all'):
    """
    Converts Ways in OSM data (stored in a file) into Points and LineString geojson features.
    Each Node is converted in a Point.
    Each Way that has 'highway' tag is converted in a LineString.
    The tags are carried over into 'properties' dictionary attached to each feature.

    Parameters
    ----------
    filename: str
        path to OSM file

    keep_tags: set or 'all'
        specifies which OSM tags should be carried over to geojson


    Returns
    -------
    dict:
        dictionary representation of the geojson

    """


    # Collect all OSM nodes
    dict_of_coords = dict()
    osm_generator = osmread.parse_file(filename)

    for item in osm_generator:
        if isinstance(item, osmread.Node):
            dict_of_coords[item.id] = (item.lon, item.lat)

    # Collect relevant features
    feature_collection = []
    osm_generator = osmread.parse_file(filename) # generator!!

    for item in osm_generator:
        if isinstance(item, osmread.Node) and item.tags != {}:
            if keep_tags == 'all':
                tags = item.tags
            else:
                tags = filter_dict(item.tags, keep_tags)

            point = Point(dict_of_coords[item.id])
            feature = Feature(geometry=point, id=item.id, properties=tags)
            feature_collection.append(feature)
        elif isinstance(item, osmread.Way) and 'highway' in item.tags:

            if keep_tags == 'all':
                tags = item.tags
            else:
                tags = filter_dict(item.tags, keep_tags)

            loc_coords = []
            for node in item.nodes:
                try:
                    loc_coords.append(dict_of_coords[node])
                except:
                    # print("this node_id {} is required, but not found in OSM!".format(node),file=sys.stderr)
                    pass

            line_string = LineString(loc_coords)
            feature = Feature(geometry=line_string, id=item.id, properties=tags)
            feature_collection.append(feature)

    geojson_file = FeatureCollection(feature_collection)
    return geojson_file


def osm_to_geojson_file(input_file, output_file):
    geojson_dict = osm_to_geojson(input_file)

    result = geojson.is_valid(geojson_dict)
    if not result['valid']:
        print('warning: the resulting geojson is not valid!')

    geojson.dump(geojson_dict, open(output_file, 'w'))