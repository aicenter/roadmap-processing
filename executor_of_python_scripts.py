import sys
import time
from prune_geojson_file import Pruning_geojson_file
from simplify_graph import Simplifying_graph
from data_from_gmaps import Data_from_gmapsAPI
from curvature import Calculation_curvature
from postprocess_geojson import Postprocessing

filename = sys.argv[1]

print "prune_geojson_file.py is running..."
start_time = time.time()

test = Pruning_geojson_file(filename)
test.load_file()
test.prune_geojson_file()
test.save_pruned_geojson()

print("time: %s secs\n" % (time.time() - start_time))

print "simplify_graph.py is running..."
start_time = time.time()

test = Simplifying_graph("data/pruned_file.geojson")
test.load_file_and_graph()
test.simplify_graph()
test.prepare_to_saving_optimized()
test.save_file_to_geojson()

print("time: %s secs\n" % (time.time() - start_time))

print "data_from_gmaps.py is running..."
start_time = time.time()

test = Data_from_gmapsAPI("data/graph_with_simplified_edges.geojson")
test.check(True)
test.load_file_and_graph()
test.get_gmaps_data()
test.save_file_to_geojson()

print("time: %s secs\n" % (time.time() - start_time))

print "curvature.py is running..."
start_time = time.time()

test = Calculation_curvature("data/result-out.geojson")
test.load_geojson()
test.analyse_roads()
test.save_geojson()

print("time: %s secs\n" % (time.time() - start_time))

print "postprocess_geojson.py is running..."
start_time = time.time()

test = Postprocessing("data/curvature-out.geojson")
test.load_geojson_and_graph()
test.export_points_to_geojson()
test.postprocessing_file()
test.is_geojson_valid()
test.save_geojson()

print("time: %s secs" % (time.time() - start_time))
