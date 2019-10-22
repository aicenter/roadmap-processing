import os.path
import networkx.algorithms.shortest_paths
import roadmaptools.utm
import roadmaptools.geometry
import roadmaptools.shp
import roadmaptools.inout
import roadmaptools.plotting

from typing import Dict, Union, Optional, List, Callable, Tuple
from networkx import DiGraph
from shapely.geometry import Point
from scipy.spatial.kdtree import KDTree
from geojson import FeatureCollection
from tqdm import tqdm
from roadmaptools.printer import print_info
from roadmaptools.road_structures import LinestringEdge, Node
from roadmaptools.utm import CoordinateConvertor


def get_node_id(node) -> str:
    lon = int(node[0] * 10 ** 6)
    lat = int(node[1] * 10 ** 6)
    if lon < 0 and lat < 0:
        return "1" + str(lon)[1:] + str(lat)[1:]
    elif lon < 0 and lat >= 0:
        return "2" + str(lon)[1:] + str(lat)
    elif lon >= 0 and lat < 0:
        return "3" + str(lon) + str(lat)[1:]
    else:
        return str(lon) + str(lat)


def _create_node(x: float, y: float, id: int) -> Node:
    return Node(x, y, id)


class RoadGraph:
    def __init__(self, use_cache: bool = True, cache_filepath: str = "",
                 node_creator: Callable[[float, float, int], Node] = _create_node):
        self.use_cache = use_cache
        self.cache_filepath = cache_filepath
        self.node_creator = node_creator
        self.graph: DiGraph = None
        self.kdtree: KDTree = None
        self.projection = None
        self.node_map: Dict[int, Node] = {}

    def load_from_geojson(self, geojson_filepath: str):
        if self.use_cache and os.path.exists(self.cache_filepath):
            self.graph = networkx.read_gpickle(self.cache_filepath)
            self.projection = roadmaptools.utm.TransposedUTM.from_zone(self.graph.graph["zone_number"],
                                                                       self.graph.graph["zone_letter"])
            CoordinateConvertor.projection = self.projection

            print_info("Projection loaded from the cache: {}{}".format(
                self.projection.origin_zone_number, self.projection.origin_zone_letter))
        else:
            geojson = roadmaptools.inout.load_geojson(geojson_filepath)

            # projection determination
            for item in geojson['features']:
                if item["geometry"]["type"] == "LineString":
                    first_coord = geojson['features'][0]['geometry']['coordinates'][0]
                    break
                    
            self.projection = roadmaptools.utm.TransposedUTM.from_gps(first_coord[1], first_coord[0])
            print_info("Projection determined from the first coordinate: {}{}".format(
                self.projection.origin_zone_number, self.projection.origin_zone_letter))
            CoordinateConvertor.projection = self.projection

            self.graph = DiGraph(zone_number=self.projection.origin_zone_number,
                                 zone_letter=self.projection.origin_zone_letter)

            edge_counter = 0

            print_info("Creating networkx graph from geojson")
            for item in tqdm(geojson['features'], desc="processing features"):
                if item["geometry"]["type"] == "LineString":
                    coords = item['geometry']['coordinates']
                    coord_from = roadmaptools.utm.wgs84_to_utm(coords[0][1], coords[0][0], self.projection)
                    coord_to = roadmaptools.utm.wgs84_to_utm(coords[-1][1], coords[-1][0], self.projection)

                    node_from = self._get_node(coord_from[0], coord_from[1])
                    node_to = self._get_node(coord_to[0], coord_to[1])

                    edge = LinestringEdge(item, CoordinateConvertor.convert, node_from, node_to)

                    # TODO legacy, remove after moving id from properties to id attribute
                    edge_id = item['properties']['id'] if "id" in item['properties'] else item['id']
                    length = item['properties']['length'] if 'length' in item['properties'] \
                        else roadmaptools.geometry.get_distance(coord_from, coord_to)

                    if node_from in self.graph and node_to in self.graph[node_from]:
                        a = 1

                    self.graph.add_edge(node_from, node_to, id=edge_id, length=length, edge=edge)

                    edge_counter += 1

            if edge_counter != len(self.graph.edges):
                a = 1

            if self.use_cache:
                networkx.write_gpickle(self.graph, self.cache_filepath)

    def get_precise_path_length(self, edge_from: LinestringEdge, edge_to: LinestringEdge,
                                point_from: Point, point_to: Point) -> Optional[float]:
        from_node = edge_from.node_to
        to_node = edge_to.node_from

        if edge_from == edge_to:
            length = roadmaptools.shp.distance_on_linestring_between_points(edge_from.linestring, point_from, point_to)
        else:
            try:
                length = networkx.algorithms.shortest_paths.astar_path_length(self.graph, from_node, to_node,
                                                                              weight="length")
            except networkx.exception.NetworkXNoPath:
                return None

            length += edge_from.linestring.length - edge_from.linestring.project(point_from)
            length += edge_to.linestring.project(point_to)

        return length

    def get_edge_path_between_edges(self, edge_from: LinestringEdge, edge_to: LinestringEdge) -> List[LinestringEdge]:
        edge_list = []

        from_node = edge_from.node_to
        to_node = edge_to.node_from
        node_list: List[Node] = networkx.algorithms.shortest_paths.astar_path(self.graph, from_node, to_node,
                                                                              weight="length")
        index = 1
        from_node = node_list[0]
        to_node = node_list[index]
        while True:
            edge = self.graph[from_node][to_node]["edge"]
            edge_list.append(edge)

            index += 1
            if index == len(node_list):
                break
            from_node = to_node
            to_node = node_list[index]

        return edge_list

    def export_for_matplotlib(self) -> Tuple[List[float], List[float]]:

        def iterator():
            for edge in self.graph.edges:
                yield ((edge[0].x, edge[1].x),(edge[0].y), edge[1].y)

        iterator = iterator()

        return roadmaptools.plotting.export_for_matplotlib(iterator)

    def _get_node(self, x: float, y: float) -> Node:
        id = roadmaptools.utm.get_id_from_utm_coords(x, y)
        if id in self.node_map:
            return self.node_map[id]
        else:
            node = self.node_creator(x, y, id)
            self.node_map[id] = node
            return node
