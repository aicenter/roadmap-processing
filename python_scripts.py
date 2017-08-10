import time
from prune_geojson_file import Pruning_geojson_file
from simplify_graph import Simplifying_graph
from data_from_gmaps import Data_from_gmapsAPI
from curvature import Calculation_curvature
from postprocess_geojson import Postprocessing
from speed_from_osm import Speed_from_osm


def clean_geojson(filename):
    print "prune_geojson_file.py is running..."
    start_time = time.time()

    test = Pruning_geojson_file(filename)
    test.load_file()
    test.prune_geojson_file()
    test.save_pruned_geojson()

    print("time: %s secs\n" % (time.time() - start_time))


def simplify_geojson(filename, simplify_lanes=False, simplify_curvature=False):
    print "simplify_graph.py is running..."
    start_time = time.time()

    test = Simplifying_graph(filename)
    test.load_file_and_graph()
    test.set_simplify_lanes(simplify_lanes)
    test.set_simplify_curvature(simplify_curvature)
    test.simplify_graph()
    test.prepare_to_saving_optimized()
    test.save_file_to_geojson()

    print("time: %s secs\n" % (time.time() - start_time))

def get_speed_from_osm(filename):
    print "speed_from_osm.py is running..."
    start_time = time.time()

    test = Speed_from_osm(filename)
    test.load_file_and_graph()
    test.get_speed()
    test.save_geojson()

    print("time: %s secs\n" % (time.time() - start_time))

def get_gmaps_information(filename, check_gmaps=True):
    print "data_from_gmaps.py is running..."
    start_time = time.time()

    test = Data_from_gmapsAPI(filename)
    test.set_check_gmaps(check_gmaps)
    test.load_file_and_graph()
    test.get_gmaps_data()
    test.save_file_to_geojson()

    print("time: %s secs\n" % (time.time() - start_time))


def get_curvature_of_edges(filename):
    print "curvature.py is running..."
    start_time = time.time()

    test = Calculation_curvature(filename)
    test.load_geojson()
    test.analyse_roads()
    test.save_geojson()

    print("time: %s secs\n" % (time.time() - start_time))


def postprocessing_geojson(filename, formated_output=False):
    print "postprocess_geojson.py is running..."
    start_time = time.time()

    test = Postprocessing(filename)
    test.load_geojson_and_graph()
    test.export_points_to_geojson()
    test.postprocessing_file()
    test.is_geojson_valid()
    test.formated(formated_output)
    test.save_geojson()

    print("time: %s secs" % (time.time() - start_time))
