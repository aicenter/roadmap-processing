import urllib2
import re
import subprocess
import os
import bz2file
import time
import sys


def map_downloader(url):
    try:
        subprocess.call(["wget", "-O", "map.osm.bz2", url])
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print "wget not found!\nplease, install it, it's available both Linux and Windows"  # handle file not found error.
        else:
            raise  # Something else went wrong while trying to run `wget`


def substring_after(s, delim):
    return s.partition(delim)[2]


URL_BASE = 'https://mapzen.com'
url = URL_BASE + '/data/metro-extracts/'

responce = urllib2.urlopen(url)

list_of_content = responce.readlines()

if len(sys.argv) > 1:
    my_city = sys.argv[1]
else:
    my_city = 'Prague'

all_cities = []
for line in list_of_content:
    if "class=\"city\"" in line:
        line = re.split("<|>", line)
        all_cities.append(line[-3])
        if line[-3] == my_city:
            city_url = substring_after(line[1], "href=")
            url = URL_BASE + city_url.replace("\"", "")

            responce = urllib2.urlopen(url)
            for line in responce.readlines():
                if "OSM XML" in line:
                    line = re.split(" |<|>", line)  # cut string into list
                    print "size:", line[-5]  # size in MB
                    downloading_page = substring_after(line[11], "=")  # http download
                    map_downloader(downloading_page.replace("\"", ""))

                    start_time = time.time()
                    bz_file = bz2file.open("map.osm.bz2")
                    with open("downloaded_map.osm", "w") as out:  # decompress bz2 file
                        out.write(bz_file.read())
                    out.close()
                    print "time:", (time.time() - start_time)
                    exit()

print "spell your city correctly, or choose another from this list: {}".format(all_cities)