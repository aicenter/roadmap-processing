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
import networkx
import roadmaptools.inout
import roadmaptools.geometry

from typing import Dict
from geojson import FeatureCollection
from tqdm import tqdm
from networkx import DiGraph
from roadmaptools.utm import CoordinateConvertor
from roadmaptools.printer import print_info
from roadmaptools.road_structures import LinestringEdge, Node

node_map: Dict[int, Node] = {}
graph: DiGraph = DiGraph()


def load_from_geojson(geojson: FeatureCollection):
	# projection determination
	first_coord = geojson['features'][0]['geometry']['coordinates']
	projection = roadmaptools.utm.TransposedUTM(first_coord[1], first_coord[0])
	print_info("Projection determined from the first coordinate: {}{}".format(
		projection.origin_zone_number, projection.origin_zone_letter))
	CoordinateConvertor.projection = projection

	print_info("Creating networkx graph from geojson")
	for item in tqdm(geojson['features'], desc="processing features"):
		if item["geometry"]["type"] == "LineString":
			coords = item['geometry']['coordinates']
			coord_from = roadmaptools.utm.wgs84_to_utm(coords[0][1], coords[0][0], projection)
			coord_to = roadmaptools.utm.wgs84_to_utm(coords[-1][1], coords[-1][0], projection)

			node_from = _get_node(coord_from[0], coord_from[1])
			node_to = _get_node(coord_to[0], coord_to[1])

			edge = LinestringEdge(item, CoordinateConvertor.convert, node_from, node_to)

			# TODO legacy, remove after moving id from properties to id attribute
			edge_id = item['properties']['id'] if "id" in item['properties'] else item['id']
			length = item['properties']['length'] if 'length' in item['properties'] \
				else roadmaptools.geometry.get_distance(coord_from, coord_to)
			graph.add_edge(node_from, node_to, id=edge_id, length=length, edge=edge)


def _get_node(x: float, y: float) -> Node:
	id = roadmaptools.utm.get_id_from_utm_coords(x, y)
	if id in node_map:
		return node_map[id]
	else:
		node = _create_node(x, y, id)
		node_map[id] = node
		return node


def _create_node(x: float, y: float, id: int) -> Node:
	return Node(x, y, id)

print_info("START STNDARD")
map = roadmaptools.inout.load_geojson(r"C:\AIC data\Shared\Map Matching Benchmark\2015 100 tracks dataset\00000043/map.geojson")
load_from_geojson(map)
print_info("END STANDARD")

networkx.write_gpickle(graph, "pi.pickle")


print_info("START_PICKLE")
networkx.read_gpickle("pi.pickle")
print_info("END PICKLE")