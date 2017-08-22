from __future__ import print_function
import time
from prune_geojson_file import Pruning_geojson_file
from simplify_graph import Simplifying_graph
from curvature import Calculation_curvature
from postprocess_geojson import Postprocessing
from speed_from_osm import Speed_from_osm
import subprocess


def execute_all_bash():
    exit_code = subprocess.call("cat data/output.geojson | python prune_geojson_file.py | python simplify_graph.py | python speed_from_osm.py | python curvature.py | python postprocess_geojson.py > data/result.geojson", shell=True)
    return exit_code

def clean_geojson():
    print("prune_geojson_file.py is running...")
    start_time = time.time()

    test = Pruning_geojson_file()
    test.load_file("data/output.geojson")
    test.prune_geojson_file()
    test.save_geojson_file("data/output-cleaned.geojson")

    print("time: %s secs\n" % (time.time() - start_time))


def simplify_geojson():
    print("simplify_graph.py is running...")
    start_time = time.time()

    test = Simplifying_graph()
    test.load_file_and_graph("data/output-cleaned.geojson")
    test.set_simplify_lanes(False)
    test.set_simplify_curvature(False)
    test.simplify_graph()
    test.prepare_to_saving_optimized()
    test.save_file_to_geojson("data/output-simplified.geojson")

    print("time: %s secs\n" % (time.time() - start_time))


def get_speed_from_osm():
    print("speed_from_osm.py is running...")
    start_time = time.time()

    test = Speed_from_osm()
    test.load_file_and_graph("data/output-simplified.geojson")
    test.get_speed()
    test.save_geojson("data/output-speeds.geojson")

    print("time: %s secs\n" % (time.time() - start_time))


def get_curvature_of_edges():
    print("curvature.py is running...")
    start_time = time.time()

    test = Calculation_curvature()
    test.load_geojson("data/output-speeds.geojson")
    test.analyse_roads()
    test.save_geojson("data/output-curvatures.geojson")

    print("time: %s secs\n" % (time.time() - start_time))


def postprocessing_geojson():
    print("postprocess_geojson.py is running...")
    start_time = time.time()

    test = Postprocessing()
    test.load_geojson_and_graph("data/output-curvatures.geojson")
    test.export_points_to_geojson()
    test.postprocessing_file()
    test.is_geojson_valid()
    test.formated(False)
    test.save_geojson("data/output-result.geojson")

    print("time: %s secs" % (time.time() - start_time))
