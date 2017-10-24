"""Set of useful tools for work with geojson file + error log."""
from __future__ import print_function
from geojson import dump, load, is_valid
from sys import stderr

__author__ = "Zdenek Bousa"
__email__ = "bousazde@fel.cvut.cz"


def save_geojson(json_dict, out_stream):
    """Save in geojson format and check for empty dictionaries."""
    json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    dump(json_dict, out_stream)


def save_geojson_formatted(json_dict, out_stream):
    """Save in geojson format, format output file and check for empty dictionaries."""
    json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
    dump(json_dict, out_stream, indent=4, sort_keys=True)


def load_geojson(in_stream):
    """Load geojson into dictionary.
    Return: dictionary"""
    return load(in_stream)


def is_geojson_valid(geojson_file):
    """Check if gejson is valid.
    Return: True/False"""
    validation = is_valid(geojson_file)
    if validation['valid'] == 'yes':
        return True
    return False


def eprint(*args, **kwargs):
    """Provides easy log on error output"""
    print(*args, file=stderr, **kwargs)
