<!--
Copyright (c) 2021 Czech Technical University in Prague.

This file is part of Roadmaptools 
(see https://github.com/aicenter/roadmap-processing).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
-->
# 5.0.0
## Changed
- clean.geojson.py updated so that osmids are kept through the process
- max speed unit is now saved in separate edge property, instead in the max speed string

## Addded
- map download from overpass by area name

## Removed
- the `osmtogeojson` script together with the broken `osmread` dependency


# 4.1.0

## Added
- delimiter option added to `inout.save_csv` method

## Fixed
- country specific speed codes extended by US codes
- string detection bug fixed in get_posted_speed method
- config bug with negative coordinates treated as float fixed in download_map.py


# 4.0.0
## Added
- GeoJSON node iterator added to plotting

## Changed
- inout.load_json now accepts encoding parameter
- GeoJSON iterator renamed to GeoJSON edge iterator

## Fixed
- GeoJSON edge iterator in plotting now handles feature collections that contains other feature types than LineStirng


# 3.0.0
## Added
- new filter module with a generic method for edge filtering
- new method export_nodes_for_matplotlib in plotting

## Changed
- method export_for_matplotlib in plotting renamed to export_edges_for_matplotlib

# 2.0.1
## Added
- Changelog

## Fixed
- utm package added to setup requirements
- readme updated
