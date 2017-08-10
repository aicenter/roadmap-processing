from __future__ import print_function
import sys
import time
import os
import subprocess
import commands
import platform
from os import listdir
from os.path import join


# stazeni dat z OSM, zavolani konvertra, nasledne osekani jen na silnice, pote dalsi uklid dat, simplifikace,
# ziskani dat z gmaps, pridani krivosti silnic, doupraveni vysledneho souboru

# params:
# -help
# -sample
# jinak 1.argument je zdroj s OSM, formatovani geojson, nastaveni kontroly dat z gmaps,
# nezjednodusovat pruhy,rozsekat podle zakriveni...(doplnit)

def err_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_all_params_osmfilter(file):
    loc_commands = ""
    for line in file:
        if line[0] != "#":
            loc_commands += line.replace("\n", " ")
    return loc_commands


def map_downloader():
    try:
        subprocess.call(["wget", "-O", "map.osm", "http://api.openstreetmap.org/api/0.6/map?bbox=14.4046,50.0691,14.4369,50.0819"])
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            err_print("wget not found!\nplease, install it, it's available both Linux and Windows")  # handle file not found error.
        else:
            raise  # Something else went wrong while trying to run `wget`

my_platform = platform.system() #get system info

if len(sys.argv) == 1:
    err_print("too few arguments!")
    exit(1)

if sys.argv[1] == '-help':
    print("usage of script..")
    print("parameters:")
    print("-help        information about functionality of script and possible parameters")
    print("-version     version of script")
    print("-sample      simple sample of functionality")
    print("1.param      OSM input")
    print("last param   remove all temporary files")
    exit(0)
elif sys.argv[1] == '-version':
    print("version: 0.0.1")
    exit(0)
elif sys.argv[1] == '-sample':
    map_downloader()
    # handle and make method for osmfilter which use first arg as input map
else:
    if not os.path.exists(sys.argv[1]):
        err_print("{} doesn't exist!".format(sys.argv[1]))
        exit(1)

start_time = time.time()
print("starting script..")

if not os.path.isdir("data"):
    os.makedirs("data")
    print("creating folder...")

if os.path.exists("data/temp_data.gpickle"):
    print("found data from previous graph...")
    responce = raw_input("do you want to delete it? [y/n]")
    if responce == "y":
        os.remove("data/temp_data.gpickle")
        print("data from previous graph was deleted...")

if os.path.exists("data/data_from_gmaps.log"):
    os.remove("data/data_from_gmaps.log")

if os.path.exists("osmfilter"):
    print("cleaning OSM data...")
    with open("config", mode='r') as f:
        args = get_all_params_osmfilter(f)
    f.close()
    # run OSMFILTER
    command = "./osmfilter {} {} > data/output.osm".format(sys.argv[1], args)
    # print(command) #check what is executed
    data = os.system(command)
else:
    err_print("osmfilter doesn't exist!\nplease, download it from: http://wiki.openstreetmap.org/wiki/Osmfilter")
    exit(1)

status, version = commands.getstatusoutput("osmtogeojson --version")
if status==0:
    print("version: {}".format(version))
else:
    print("trying to install osmtogeojson...")
    try:
        if my_platform=="Linux":
            subprocess.call(["sudo","npm", "install", "-g","osmtogeojson"])
        elif my_platform=="Windows":
            subprocess.call(["npm", "install", "-g", "osmtogeojson"])
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            err_print("npm not found! please install it first...")
        else:
            raise

#run pipeline.......
os.system("python2.7 executor_of_python_scripts.py data/output.geojson")

if sys.argv[-1]=='-r':
    print("removing temporary files...")
    os.remove("data/output.osm")
    os.remove("data/output.geojson")
    os.remove("data/deleted_items.geojson")
    os.remove("data/pruned_file.geojson")
    os.remove("data/graph_with_simplified_edges.geojson")
    os.remove("data/result-out.geojson")
    os.remove("data/curvature-out.geojson")


dir = os.path.dirname(os.path.abspath(__file__))
files=os.listdir(dir)

for item in files:
    if item.endswith(".pyc"):
        os.remove(join(dir, item))

print("finished in time: {}".format(time.time()-start_time))