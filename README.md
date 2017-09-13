# roadmap-processing

Python's tool for processing mostly geoJSON files and also OSM files. 

### Prerequisites

We will work with [pip](https://pypi.python.org/pypi/pip), [wget](https://www.gnu.org/software/wget/) and [virtualenv](https://virtualenv.pypa.io/en/stable/)(optional). You can follow steps below to install it properly.

### Installing

Use

```
python get-pip.py
```

for installing pip and

```
sudo pip install virtualenv
```

for virtualenv or eventually on Windows use


```
pip install virtualenv
```

If you are running in Linux, type


```
mkdir ~/virtualEnvironment && cd ~/virtualEnvironment
```

then clone this GitHub project

```
git clone https://github.com/aicenter/roadmap-processing.git
```
or clone with ssh
```
git clone git@github.com:aicenter/roadmap-processing.git
```

and finally use

```
virtualenv --python path/to/python2.7/interpreter --no-site-packages --distribute .env && source .env/bin/activate
```

where you subtitute path/to/python2.7/interpreter with your own path to python 2.7 interpreter to create isolated Python environment.

This project is also available on PyPI and it is recommended install it as package

```
pip install roadmaptools
```

## Examples of usage

Almost in every script there are two ways how to run it or get resulting geoJSON.

osmtogeojson (description: convert OSM file to geoJSON file)

```python
   from roadmaptools import osmtogejson

   geojson_file = osmtogeojson.convert_osmtogeojson("path/to/OSMfile.osm")
   osmtogeojson.is_geojson_valid(geojson_file) # return 'yes' or 'no'
   f = open("path/to/output_file.geojson","w")
   osmtogeojson.save_geojson(geojson_file,f)
   f.close()
```

clean_geojson (description: get only LineStrings, where everyone has only 2 coordinates; check important features, whether are meaningful)

```python
   from roadmaptools import clean_geojson

   f = open("path/to/input_file.geojson","r")
   geojson_file = clean_geojson.load_geojson(f)
   f.close()

   geojson_unused = clean_geojson.get_geojson_with_deleted_features(geojson_file) # Points and Polygons etc.
   geojson_out = clean_geojson.get_cleaned_geojson(geojson_file)
   f = open("path/to/output_file.geojson","w")
   clean_geojson.save_geojson(geojson_out,f)
   f.close()
```

simplify_graph (description: default - create graph, where nodes are only in crossroads; l_check - create graph, where nodes are also in way, where number of lanes is changing; c_check - according to thresholds create graph, where nodes are also in way, where curvature exceeds the threshold)

```python
   from roadmaptools import simplify_graph

   f = open("path/to/input_file.geojson","r")
   geojson_file = simplify_graph.load_geojson(f)
   f.close()

   thrs = simplify_graph.thresholds # optional
   simplify_graph.thresholds = [0,1,2] # optional
   geojson_out = simplify_graph.get_simplified_geojson(geojson_file) # (optional arguments) l_check - > set True to do not simplify roads with same number of lanes, c_check -> set True to do not simplify roads with different curvature
   f = open("path/to/output_file.geojson","w")
   simplify_graph.save_geojson(geojson_out,f)
   f.close()
```

estimate_speed_from_osm (description: add information about speed from [OSM](http://wiki.openstreetmap.org/wiki/Key:maxspeed), if maxspeed is not available, some heuristics are used)

```python
   from roadmaptools import estimate_speed_from_osm

   f = open("path/to/input_file.geojson","r")
   geojson_file = estimate_speed_from_osm.load_geojson(f)
   f.close()

   geojson_out = estimate_speed_from_osm.get_geojson_with_speeds(geojson_file)
   f = open("path/to/output_file.geojson","w")
   estimate_speed_from_osm.save_geojson(geojson_out,f)
   f.close()
```

calculate_curvature (description: add information about curvature, it is calculated from GPS)

```python
   from roadmaptools import calculate_curvature

   f = open("path/to/input_file.geojson","r")
   geojson_file = calculate_curvature.load_geojson(f)
   f.close()

   geojson_out = calculate_curvature.get_geojson_with_curvature(geojson_file)
   f = open("path/to/output_file.geojson","w")
   calculate_curvature.save_geojson(geojson_out,f)
   f.close()
```

export_nodes_and_id_maker (description: create new geoJSON file with all intersections (nodes), generate unique ID for each node and add direction (from node, to node) for each way)

```python
   from roadmaptools import export_nodes_and_id_maker

   f = open("path/to/input_file.geojson","r")
   geojson_file = calculate_curvature.load_geojson(f)
   f.close()

   points = export_nodes_and_id_maker.export_points_to_geojson(geojson_file)
   f = open("path/to/output_file_nodes.geojson","w")
   export_nodes_and_id_maker.save_geojson(points,f,is_formated=True) # in this script it is possible to save geojson in read-friendly mode
   f.close()

   geojson_out = export_nodes_and_id_maker.get_geojson_with_unique_ids(geojson_file)
   f = open("path/to/output_file_edges.geojson","w")
   export_nodes_and_id_maker.save_geojson(geojson_out,f,is_formated=False) # False is default
   f.close()
```

prepare_geojson_to_agentpolisdemo (description: get the biggest strongly connected component and suppress multiple ways between two nodes (i.e. simplified graph is now broken)

```python
   from roadmaptools import prepare_geojson_to_agentpolisdemo

   f = open("path/to/input_file.geojson","r")
   geojson_file = prepare_geojson_to_agentpolisdemo.load_geojson(f)
   f.close()

   geojson_list_out = prepare_geojson_to_agentpolisdemo.get_nodes_and_edges_for_agentpolisdemo(geojson_file) # return [edges, nodes]
   f = open("path/to/output_file_edges.geojson","w")
   prepare_geojson_to_agentpolisdemo.save_geojson(geojson_list_out[0],f)
   f.close()

   f = open("path/to/output_file_nodes.geojson","w")
   prepare_geojson_to_agentpolisdemo.save_geojson(geojson_list_out[1],f)
   f.close()
```

## Versioning

We use [GitHub](https://github.com) for versioning. For the versions available, see the [tags on this repository](https://github.com/aicenter/roadmap-processing/tags). 

## Authors

* **Martin Korytak** - *Initial work*

See also the list of [contributors](https://github.com/aicenter/roadmap-processing/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details

