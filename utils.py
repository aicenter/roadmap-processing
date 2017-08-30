from __future__ import print_function
import os
import subprocess
import platform
from os.path import join
import sys
import argparse



# print to STDERR
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
            err_print("wget not found!\nplease, install it, it's available both Linux and Windows")  # handle file not found error
        else:
            raise  # something else went wrong while trying to run `wget`


# check whether osmfilter exists, else download it
def check_osmfilter(osmfilter_version, is_linux, mapfile):
    if os.path.exists(osmfilter_version):
        with open("config", mode='r') as f:
            args = get_all_params_osmfilter(f)
        f.close()
        if is_linux:
            command = "./osmfilter {} {} > data/output.osm".format(mapfile, args)
        else:
            command = "osmfilter.exe {} {} > data/output.osm".format(mapfile, args)
        # print(command) #check what is executed
        os.system(command)
    else:
        print("downloading osmfilter...")
        if is_linux:
            os.system("wget -O - http://m.m.i24.cc/osmfilter.c |cc -x c - -O3 -o osmfilter")
            check_osmfilter("osmfilter", is_linux, mapfile)
        else:
            osmfilter_downloader("m.m.i24.cc/osmfilter.exe")
            check_osmfilter("osmfilter.exe", is_linux, mapfile)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('MAP', type=str, action='store', help='input map in OSM format')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.2')
    parser.add_argument('-r', action='store_true',default=False,dest='boolean',help='remove all temporary files')
    return parser.parse_args()

def configure_and_download_dependecies():
    my_platform = platform.system()  # get system info

    # if len(argv) == 1:  # at least one param
    #     err_print("too few arguments!")
    #     exit(1)
    #
    # if argv[1] == '-help':  # get help
    #     print("usage of script..")
    #     print("parameters:")
    #     print("-help                    information about functionality of script and possible parameters")
    #     print("-version                 version of script")
    #     print("1.param (compulsory)     OSM input file")
    #     print("-r (optional)            remove all temporary files")
    #     exit(0)
    # elif argv[1] == '-version':  # get version
    #     print("version: 0.1.2")
    #     exit(0)
    # else:  # check if path to map is correct
    #     if not os.path.exists(argv[1]):
    #         err_print("{} doesn't exist!".format(argv[1]))
    #         exit(1)

    # parser = argparse.ArgumentParser()
    # parser.add_argument('map', nargs='?',default=os.getcwd(),type=str,action="store",help='input map in OSM format')
    # parser.add_argument('--version', action='version',version='%(prog)s 0.1.2')
    results = get_args()

    if not os.path.exists(results.MAP):
        err_print("{} doesn't exist!".format(results.MAP))
        exit(1)

    if not os.path.isdir("data"):  # make directory data if and only if doesn't exist
        os.makedirs("data")
        print("creating folder...")

    if os.path.exists("data/temp_data.gpickle"):  # ask for removing old temporary Google Maps data
        print("found data from previous graph...")
        responce = raw_input("do you want to delete it? [y/n]")
        if responce == "y":
            os.remove("data/temp_data.gpickle")
            print("data from previous graph was deleted...")

    if os.path.exists("data/log.log"):  # remove log file with Google Maps errors
        os.remove("data/log.log")

    print("cleaning OSM data...")
    if my_platform == "Linux":  # check if osmfilter is downloaded
        check_osmfilter("osmfilter", True, results.MAP)
    elif my_platform == "Windows":
        check_osmfilter("osmfilter.exe", False, results.MAP)

    print("converting OSM to geoJSON...")

    from osmtogeojson import osmtogeojson_converter  # avoid circular dependent import
    osmtogeojson_converter("data/output.osm")


def remove_temporary_files():
    results = get_args()
    if results.boolean==True:
        print("removing temporary files...")
        os.remove("data/output.osm")
        os.remove("data/output.geojson")
        os.remove("data/deleted_items.geojson")
        os.remove("data/output-cleaned.geojson")
        os.remove("data/output-simplified.geojson")
        os.remove("data/output-speeds.geojson")
        os.remove("data/output-curvatures.geojson")


def remove_pyc_files():
    working_dir = os.path.dirname(os.path.abspath(__file__))  # remove temporary python files
    files = os.listdir(working_dir)

    for item in files:
        if item.endswith(".pyc"):
            os.remove(join(working_dir, item))
