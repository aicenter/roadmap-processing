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
import roadmaptools.inout
import geojson.feature
import networkx as nx
import roadmaptools.utm
import roadmaptools.geometry
import roadmaptools.estimate_speed_from_osm

from typing import List, Dict
from roadmaptools.init import config


_computations = []


def compute_edge_parameters(input_filename: str, output_filename: str):
	geojson_content = roadmaptools.inout.load_geojson(input_filename)

	# projection determination
	for item in geojson_content['features']:
		if item["geometry"]["type"] == "LineString":
			first_coord = item['geometry']['coordinates'][0]
			break

	projection = roadmaptools.utm.TransposedUTM.from_gps(first_coord[1], first_coord[0])

	for item in geojson_content['features']:
		# transformed coordianates
		coords = item['geometry']['coordinates']
		projected_coords = []
		for coord in coords:
			projected_coords.append(roadmaptools.utm.wgs84_to_utm_1E2(coord[1], coord[0]))
		item['properties']['utm_coords'] = projected_coords

		# edge length
		item['properties']["length"] = roadmaptools.geometry.get_length_from_coords(projected_coords)

		# max speed
		speed, unit = roadmaptools.estimate_speed_from_osm.get_posted_speed(item)
		item['properties']['maxspeed'] = speed
		item['properties']['speed_unit'] = unit


	# graph = roadmaptools.inout.load_graph(geojson_content)

	# edge_map = _create_edge_map(graph)

	# graph_multi_test(graph)

	# _computations.append(compute_centrality)

	# for computation in _computations:
	# 	computation(graph, geojson_content, edge_map)

	roadmaptools.inout.save_geojson(geojson_content, output_filename)


def compute_centrality(graph: nx.DiGraph, data: geojson.feature.FeatureCollection, edge_map: Dict):
	for item in data['features']:
		edge = edge_map[item['properties']['id']]
		from_degree = graph.degree(edge[0])
		to_degree = graph.degree(edge[1])
		item['properties']["from_degree"] = from_degree
		item['properties']["to_degree"] = to_degree


def _create_edge_map(graph: nx.DiGraph) -> Dict:
	edge_map = {}
	for edge in graph.edges():
		# edge_map[graph[edge[0]][edge[1]][0]["id"]] = edge
		edge_map[graph[edge[0]][edge[1]]["id"]] = edge
	return edge_map


def graph_multi_test(graph: nx.DiGraph):
	for edge in graph.edges():
		if len(graph[edge[0]][edge[1]]) > 1:
			a=1
