#!/usr/bin/env bash
#
# Clean OSM file -> convert to geoJSON -> simplify edges (roads) -> get velocity from googlemaps for # three types (best_guess,pessimistic,optimistic)
#

start=`date +%s`

echo "starting..."

if [ ! -d "data" ]; then
	mkdir "data"
fi

if [ -e data/temp_data.gpickle ]; then
	echo "found data from previous graph..."
	echo -n "do you want to delete them? [y/n]"
	read responce
	if [ $responce == "y" ]; then
		rm data/temp_data.gpickle
	fi
fi

if [ -e data/data_from_gmaps.log ]; then
	rm data/data_from_gmaps.log
fi

if [ -e "$1" ]; then
	if [ -e "osmfilter" ]; then
		echo "cleaning OSM data..."
		config_file="`grep -v '^#' config`"
		#echo "$config_file"  #check what is loaded
		command="./osmfilter "$1" "$config_file" > data/output.osm"
		#echo "$command" #check what will be executed
		eval $command
	else
		echo >&2 "osmfilter doesn't exist!"
		exit 1		
	fi
else
	echo >&2 "input file doesn't exist!"
	exit 1		
fi

type osmtogeojson >/dev/null 2>&1 || { echo >&2 "osmtogeojson is required, but it's not installed!"; exit 1; }
echo "converting OSM to geoJSON..."
osmtogeojson data/output.osm > data/output.geojson

type python2.7 >/dev/null 2>&1 || { echo >&2 "python2.7 is required, but it's not installed!"; exit 1; }
echo "starting python scripts..."
echo ""
python2.7 executor_of_python_scripts.py data/output.geojson


if [ $# -eq 2 ] && [ "$2" == "-r" ]; then
	echo "removing unused files..."
	rm data/output.osm
	rm data/output.geojson
	rm data/deleted_items.geojson
	rm data/pruned_file.geojson
	rm data/graph_with_simplified_edges.geojson
	rm data/result-out.geojson
	rm data/curvature-out.geojson
fi

find . -name '*.pyc' -delete

end=`date +%s`
runtime=$((end-start))
echo "finished in time: $runtime secs."
