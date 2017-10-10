"""Groups of values for OSM key = highway"""

__author__ = "Zdenek Bousa"
__email__ = "bousazde@fel.cvut.cz"


def get_road_elements_agentpolis():
    return {'primary', 'secondary', 'motorway', 'trunk', 'tertiary', 'road',
            'motorway_link', 'trunk_link', 'primary_link', 'secondary_link',
            'tertiary_link', 'residential'}


def get_road_elements_main():
    return {'primary', 'secondary', 'motorway', 'trunk', 'road',
            'motorway_link', 'trunk_link', 'primary_link', 'secondary_link',
            'tertiary_link'}


def get_road_elements_all():
    return {'primary', 'secondary', 'motorway', 'trunk', 'road', 'tertiary',
            'motorway_link', 'trunk_link', 'primary_link', 'secondary_link',
            'tertiary_link', 'unclassified', 'residential', 'service', 'living_street', 'road'
            }


def get_pedestrian_elements():
    return {'living_street', 'pedestrian', 'footway', 'bridleway', 'steps', 'path'}


def get_other_non_road_elements():
    return {'cycleway', 'proposed', 'construction', 'rest_area', 'services'}