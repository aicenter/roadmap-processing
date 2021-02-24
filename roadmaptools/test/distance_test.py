#
# Copyright (c) 2021 Czech Technical University in Prague.
#
# This file is part of Roadmaptools 
# (see https://github.com/aicenter/roadmap-processing).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from roadmaptools.init import config

import roadmaptools.inout
import roadmaptools.estimate_speed_from_osm
import roadmaptools.geojson_shp
import roadmaptools.utm

# from roadmaptools.


def coordinate_convertor(latitude: float, longitude: float):
	return roadmaptools.utm.wgs84_to_utm(latitude, longitude, projection)


def compute_length_projected(geojson_linestring):
	shp_linestring = roadmaptools.geojson_shp.geojson_linestring_to_shp_linestring(geojson_linestring,
			coordinate_convertor)

	return shp_linestring.length
	# length = 0
	# for i in range(0, len(coords) - 1):
	# 	point1 = coords[i]
	# 	point2 = coords[i + 1]
	#
	#
	#
	# 	length += get_distance_between_coords(point1, point2)
	#
	# return length


# load map
map_geojson = roadmaptools.inout.load_geojson(r"C:\AIC data\Shared\amod-data\agentpolis-experiment\Prague\experiment\ridesharing_itsc_2018\maps/map-simplified-speed.geojson")

# get some random edges
features = map_geojson['features']

edge_indexes = [0, 11, 55, 506]

projection = None

# for each edge
for index in edge_indexes:
	edge = features[index]

	if not projection:
		first_coord = edge['geometry']['coordinates'][0]
		projection = roadmaptools.utm.TransposedUTM(first_coord[1], first_coord[0])

	# compute distance from gps
	length_gps = roadmaptools.estimate_speed_from_osm.get_length(edge['geometry']['coordinates'])

	# compute distance projected
	length_projected = compute_length_projected(edge)

	print("edge {} (id: {}) - length gps: {}, length projected: {}".format(index, edge["id"], length_gps, length_projected))

a = 1;