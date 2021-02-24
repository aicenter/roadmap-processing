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
import geojson
import sys
import os.path

from typing import Tuple, List
from rtree import index
from tqdm import tqdm
from networkx import DiGraph
from shapely.geometry import Polygon, Point
from roadmaptools.printer import print_info
from roadmaptools.road_structures import LinestringEdge
from roadmaptools.graph import RoadGraph


class RoadGraphRtree:
    def __init__(self, road_graph: RoadGraph, search_size: int = 500, path: str = None):
        self.search_size = search_size
        self.index = self._build_index(road_graph, path)

    @staticmethod
    def _build_index(road_graph: RoadGraph, path: str = None):
        if path:
            cache_ready = os.path.isfile(path + ".idx")
            idx = index.Index(path)
        else:
            cache_ready = False
            idx = index.Index()
        if not cache_ready:
            print_info("Creating R-tree from geojson roadmap")
            for from_node, to_node, data in tqdm(road_graph.graph.edges(data=True), desc="processing edges"):
                edge: LinestringEdge = data["edge"]
                # data["attr"]["from"] = from_node
                # data["attr"]["to"] = to_node
                idx.insert(data["id"], edge.linestring.bounds, edge)
            if path:
                idx.close()
                idx = index.Index(path)
        return idx

    def get_nearest_edge(self, point: Point):
        search_bounds = Point(point).buffer(self.search_size).bounds
        candidates = self.index.intersection(search_bounds, objects='raw')
        min_distance = sys.maxsize
        nearest = None
        for candidate in candidates:
            edge: LinestringEdge = candidate
            distance = point.distance(edge.linestring)
            if distance < min_distance:
                min_distance = distance
                nearest = edge

        if not nearest:
            print_info("No edge found in specified distance ({} m).".format(self.search_size))

        envelope = Polygon(((search_bounds[0], search_bounds[3]), (search_bounds[2], search_bounds[3]),
                            (search_bounds[2], search_bounds[1]), (search_bounds[0], search_bounds[1])))
        if not envelope.intersects(nearest.linestring):
            print_info("solution does not have to be exact")

        return nearest

    def get_edges_in_area(self, area_bounds: Polygon) -> List[LinestringEdge]:
        # edges whose bounding box intersects the area
        potential_edges_in_area = self.index.intersection(area_bounds.bounds, objects='raw')

        edges_in_area = []
        for candidate in potential_edges_in_area:
            if area_bounds.intersects(candidate.linestring):
                edges_in_area.append(candidate)
        return edges_in_area
