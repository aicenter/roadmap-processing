from __future__ import print_function
from install_requirements import is_dependencies_satisfied
import sys

if not is_dependencies_satisfied():
    print("some packages are missing, please type: \"python install_requirements.py\"", file=sys.stderr)
    exit(1)
from python_scripts import postprocessing_geojson, get_curvature_of_edges, simplify_geojson, clean_geojson, get_speed_from_osm,execute_all_bash
from utils import configure_and_download_dependecies, remove_temporary_files, remove_pyc_files
import time

start_time = time.time()
print("starting script..")

configure_and_download_dependecies()

# run pipeline...
print("starting python scripts...\n")
code = execute_all_bash()
if code != 0:
    clean_geojson()  # remove all unused features from map
    simplify_geojson()  # simplify edges of graph, (optional) 2.param=simplification lanes and 3.param=simplification curvature
    get_speed_from_osm()  # get speed from OSM data, if missing use heuristic
    get_curvature_of_edges()  # add avarage value of curvature in single edge
    postprocessing_geojson()  # extract all intersections of edges in file,validation of geojson file, (optional) 2.param=formated output file

# if sys.argv[-1] == '-r':  # removing temporary files
remove_temporary_files() #if it is required ("-r" argument)

remove_pyc_files()

print("finished in time: {}".format(time.time() - start_time))
