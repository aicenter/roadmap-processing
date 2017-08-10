from __future__ import print_function
import sys
import time
import os
import subprocess
import commands
import platform
from os import listdir
from os.path import join
from executor_of_python_scripts import Executor_pipeline


# util for print on STDERR
def err_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# parser of configuration file
def get_all_params_osmfilter(file):
    loc_commands = ""
    for line in file:
        if line[0] != "#":
            loc_commands += line.replace("\n", " ")
    return loc_commands


# download osmfilter based on current system
def osmfilter_downloader(url_adress):
    try:
        subprocess.call(["wget", url_adress])
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            err_print("wget not found!\nplease, install it, it's available both Linux and Windows")  # handle file not found error.
        else:
            raise  # something else went wrong while trying to run `wget`


def map_downloader():
    # elif sys.argv[1] == '-sample':
    #     map_downloader()
    # handle and make method for osmfilter which use first arg as input map
    try:
        subprocess.call(["wget", "-O", "map.osm", "http://api.openstreetmap.org/api/0.6/map?bbox=14.4046,50.0691,14.4369,50.0819"])
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            err_print("wget not found!\nplease, install it, it's available both Linux and Windows")  # handle file not found error.
        else:
            raise  # Something else went wrong while trying to run `wget`


# check whether osmfilter exists, else download it
def check_osmfilter(osmfilter_version, is_linux):
    if os.path.exists(osmfilter_version):
        with open("config", mode='r') as f:
            args = get_all_params_osmfilter(f)
        f.close()
        # run OSMFILTER
        if is_linux:
            command = "./osmfilter32 {} {} > data/output.osm".format(sys.argv[1], args)
        else:
            command = "osmfilter.exe {} {} > data/output.osm".format(sys.argv[1], args)
        # print(command) #check what is executed
        os.system(command)
    else:
        print("downloading osmfilter...")
        if is_linux:
            osmfilter_downloader("m.m.i24.cc/osmfilter32")
            os.system("chmod +x osmfilter32")
            check_osmfilter("osmfilter32", is_linux)
        else:
            osmfilter_downloader("m.m.i24.cc/osmfilter.exe")
            check_osmfilter("osmfilter.exe", is_linux)


my_platform = platform.system()  # get system info

if len(sys.argv) == 1:  # at least one param
    err_print("too few arguments!")
    exit(1)

if sys.argv[1] == '-help':  # get help
    print("usage of script..")
    print("parameters:")
    print("-help        information about functionality of script and possible parameters")
    print("-version     version of script")
    print("1.param (compulsury)     OSM input file")
    print("-r (optional)   remove all temporary files")
    exit(0)
elif sys.argv[1] == '-version':  # get version
    print("version: 0.0.1")
    exit(0)
else:  # check if path to map is correct
    if not os.path.exists(sys.argv[1]):
        err_print("{} doesn't exist!".format(sys.argv[1]))
        exit(1)

start_time = time.time()
print("starting script..")

if not os.path.isdir("data"):  # make directory data if and only if doesn't exist
    os.makedirs("data")
    print("creating folder...")

if os.path.exists("data/temp_data.gpickle"):  # ask for removing old temporary Google Maps data
    print("found data from previous graph...")
    responce = raw_input("do you want to delete it? [y/n]")
    if responce == "y":
        os.remove("data/temp_data.gpickle")
        print("data from previous graph was deleted...")

if os.path.exists("data/data_from_gmaps.log"):  # remove log file with Google Maps errors
    os.remove("data/data_from_gmaps.log")

print("cleaning OSM data...")
if my_platform == "Linux":  # check if osmfilter is downloaded
    check_osmfilter("osmfilter32", is_linux=True)
elif my_platform == "Windows":
    check_osmfilter("osmfilter.exe", is_linux=False)

print("converting OSM to geoJSON...")
status, version = commands.getstatusoutput("osmtogeojson --version")  # check if osmtogeojson is installed
if status == 0:
    print("version: {}".format(version))
    os.system("osmtogeojson data/output.osm > data/output.geojson")
else:
    print("trying to install osmtogeojson...")
    try:  # try install it and run
        if my_platform == "Linux":
            subprocess.call(["sudo", "npm", "install", "-g", "osmtogeojson"])
        elif my_platform == "Windows":
            subprocess.call(["npm", "install", "-g", "osmtogeojson"])
        os.system("osmtogeojson data/output.osm > data/output.geojson")
        print("installation and converting was successful...")
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            err_print("npm not found! please install it first...")
        else:
            raise

# run pipeline...
print("starting python scripts...\n")
executor = Executor_pipeline()
executor.clean_geojson("data/output.geojson")  # remove all unused features from map
executor.simplify_geojson("data/pruned_file.geojson")  # simplify edges of graph, (optional) 2.param=simplification lanes and 3.param=simplification curvature
executor.get_gmaps_information("data/graph_with_simplified_edges.geojson")  # get data about speed, length and duration of all roads in map, (optional) 2.param=check correctness of gmaps results
executor.get_curvature_of_edges("data/gmaps-out.geojson")  # add avarage value of curvature in single edge
executor.postprocessing("data/curvature-out.geojson")  # extract all intersections of edges in file,validation of geojson file, (optional) 2.param=formated output file

if sys.argv[-1] == '-r':  # removing temporary files
    print("removing temporary files...")
    os.remove("data/output.osm")
    os.remove("data/output.geojson")
    os.remove("data/deleted_items.geojson")
    os.remove("data/pruned_file.geojson")
    os.remove("data/graph_with_simplified_edges.geojson")
    os.remove("data/result-out.geojson")
    os.remove("data/curvature-out.geojson")

dir = os.path.dirname(os.path.abspath(__file__))  # remove temporary python files
files = os.listdir(dir)

for item in files:
    if item.endswith(".pyc"):
        os.remove(join(dir, item))

print("finished in time: {}".format(time.time() - start_time))
