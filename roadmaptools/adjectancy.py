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
import numpy as np
import roadmaptools.inout

from typing import List, Callable
from tqdm import tqdm
from geojson import FeatureCollection


def create_adj_matrix(nodes_filepath: str, edges_filepath: str, out_filepath: str,
					  cost_function: Callable[[dict], int]):
	nodes = roadmaptools.inout.load_geojson(nodes_filepath)
	edges = roadmaptools.inout.load_geojson(edges_filepath)
	dm = get_adj_matrix(nodes, edges, cost_function)
	roadmaptools.inout.save_csv(dm, out_filepath)


def get_adj_matrix(nodes: FeatureCollection, edges: FeatureCollection,
				   cost_function: Callable[[dict], int]) -> np.ndarray:
	nodes = nodes['features']
	size = len(nodes)
	adj = np.full((size, size), np.nan)
	node_dict = {node['properties']['node_id']: node for node in nodes}
	for edge in tqdm(edges['features'], desc='filling the adjectancy matrix'):
		from_node = node_dict[edge['properties']['from_id']]
		to_node = node_dict[edge['properties']['to_id']]
		# cost = edge['properties']['length']
		cost = cost_function(edge)
		adj[from_node['properties']['index'], to_node['properties']['index']] = cost

	return adj

