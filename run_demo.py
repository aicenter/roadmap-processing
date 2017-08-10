from executor_of_python_scripts import postprocessing_geojson,get_curvature_of_edges,simplify_geojson,clean_geojson,get_speed_from_osm
from utils import configure_and_download_dependecies,remove_temporary_files,remove_pyc_files
import sys
import time

start_time = time.time()
print("starting script..")

configure_and_download_dependecies(sys.argv)

# run pipeline...
print("starting python scripts...\n")
clean_geojson("data/output.geojson")  # remove all unused features from map
simplify_geojson("data/pruned_file.geojson")  # simplify edges of graph, (optional) 2.param=simplification lanes and 3.param=simplification curvature
get_speed_from_osm("data/graph_with_simplified_edges.geojson") #get speed from OSM data, if missing use heuristic
get_curvature_of_edges("data/speeds-out.geojson")  # add avarage value of curvature in single edge
postprocessing_geojson("data/curvature-out.geojson")  # extract all intersections of edges in file,validation of geojson file, (optional) 2.param=formated output file

if sys.argv[-1] == '-r':  # removing temporary files
    remove_temporary_files()

remove_pyc_files()

print("finished in time: {}".format(time.time() - start_time))
