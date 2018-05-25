import geojson
import osmread
from geojson import Point, LineString, Feature, FeatureCollection

from roadmaptools.util import filter_dict


DEFAULT_KEEP_TAGS = {'highway', 'id', 'lanes', 'maxspeed', 'oneway', 'bridge', 'width', 'tunnel',
                'traffic_calming', 'lanes:forward', 'lanes:backward', 'junction'}

import sys
from datetime import datetime
from time import mktime
try:
    from lxml.etree import iterparse
except ImportError:
    from xml.etree.ElementTree import iterparse

from osmread.parser import Parser
from osmread.elements import Node, Way, Relation, RelationMember

# Support for Python 3.x & 2.x
if sys.version_info > (3,):
    long = int
    unicode = str

class CustomXmlParser(Parser):

    def __init__(self, **kwargs):
        Parser.__init__(self, **kwargs)
        self._compression = kwargs.get('compression', None)

    def parse(self, fp):
        context = iterparse(fp, events=('start', 'end'))

        # common
        _type = None
        _id = None
        _version = None
        _changeset = None
        _timestamp = None
        _uid = None
        _tags = None
        # node only
        _lon = None
        _lat = None
        # way only
        _nodes = None
        # relation only
        _members = None

        for event, elem in context:

            if event == 'start':
                attrs = elem.attrib
                if elem.tag in ('node', 'way', 'relation'):
                    _id = long(attrs['id'])
                    if 'version' in attrs:
                        _version = int(attrs['version'])
                    if 'changeset' in attrs:
                        _changeset = int(attrs['changeset'])
                    # TODO: improve timestamp parsing - dateutil too slow
                    if 'timestamp' in attrs:
                        _tstxt = attrs['timestamp']
                        _timestamp = int((
                            datetime(
                                year=int(_tstxt[0:4]),
                                month=int(_tstxt[5:7]),
                                day=int(_tstxt[8:10]),
                                hour=int(_tstxt[11:13]),
                                minute=int(_tstxt[14:16]),
                                second=int(_tstxt[17:19]),
                                tzinfo=None
                            ) - datetime(
                                year=1970,
                                month=1,
                                day=1,
                                tzinfo=None
                            )
                        ).total_seconds())

                    try: #An object can miss an uid (when anonymous edits were possible)
                        _uid = int(attrs['uid'])
                    except:
                        uid = 0

                    _tags = {}

                    if elem.tag == 'node':
                        _type = Node
                        _lon = float(attrs['lon'])
                        _lat = float(attrs['lat'])
                    elif elem.tag == 'way':
                        _type = Way
                        _nodes = []
                    elif elem.tag == 'relation':
                        _type = Relation
                        _members = []

                elif elem.tag == 'tag':
                    _tags[unicode(attrs['k'])] = unicode(attrs['v'])

                elif elem.tag == 'nd':
                    _nodes.append(long(attrs['ref']))

                elif elem.tag == 'member':
                    _members.append(
                        RelationMember(
                            unicode(attrs['role']),
                            {
                                'node': Node,
                                'way': Way,
                                'relation': Relation
                            }[attrs['type']],
                            long(attrs['ref'])
                        )
                    )

            elif event == 'end':
                if elem.tag in ('node', 'way', 'relation'):
                    args = [
                        _id, _version, _changeset,
                        _timestamp, _uid, _tags
                    ]

                    if elem.tag == 'node':
                        args.extend((_lon, _lat))

                    elif elem.tag == 'way':
                        args.append(tuple(_nodes))

                    elif elem.tag == 'relation':
                        args.append(tuple(_members))

                    elem.clear()

                    yield _type(*args)


def parse_file(filename, **kwargs):
    parser_cls = None
    kwargs = dict(kwargs)

    if filename.endswith(('.osm', '.xml', '.osm.bz2', '.xml.bz2')) \
            or kwargs.get('format', None) == 'xml':

        from osmread.parser.xml import XmlParser
        parser_cls = CustomXmlParser

        if filename.endswith('.bz2'):
            kwargs['compression'] = 'bz2'

    elif filename.endswith('.pbf') \
            or kwargs.get('format', None) == 'pbf':

        from osmread.parser.pbf import PbfParser
        parser_cls = PbfParser

    parser = parser_cls(**kwargs)

    for e in parser.parse_file(filename):
        yield e


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
    osm_generator = parse_file(filename)

    for item in osm_generator:
        if isinstance(item, osmread.Node):
            dict_of_coords[item.id] = (item.lon, item.lat)

    # Collect relevant features
    feature_collection = []
    osm_generator = parse_file(filename) # generator!!

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