# code from https://stackoverflow.com/questions/46170577/find-closest-line-to-each-point-on-big-dataset-possibly-using-shapely-and-rtree
import geojson
import sys

from typing import Tuple
from rtree import index
from tqdm import tqdm
from networkx import MultiDiGraph
from shapely.geometry import Polygon, Point
from roadmaptools.printer import print_info


class RoadGraphRtree:

	def __init__(self, road_graph: MultiDiGraph, search_size=20):
		self.search_size = search_size
		self.index = self._build_index(road_graph)

	@staticmethod
	def _build_index(road_graph: MultiDiGraph):
		print_info("Creating R-tree from geojson roadmap")
		idx = index.Index()
		for edge in tqdm(road_graph.edges(), desc="processing edges"):
			idx.insert(edge["properties"]["id"], edge["geometry"].bounds(), edge)
		return idx

	def get_nearest_edge(self, point: Point):
		search_bounds = Point(point).buffer(self.search_size).bounds()
		candidates = self.index.intersection(search_bounds, objects='raw')
		min_distance = sys.maxsize
		nearest = None
		for candidate in candidates:
			distance = point.distance(candidate["shape"])
			if distance < min_distance:
				min_distance = distance
				nearest = candidate

		if not nearest:
			print_info("no edge found in specified distance")

		envelope = Polygon([[p.x, p.y] for p in search_bounds])
		if not envelope.intersects(nearest["shape"]):
			print_info("solution does not have to be exact")

		return nearest


def get_solution(idx, points):
    result = {}
    for p in points:
        pbox = (p[0]-MIN_SIZE, p[1]-MIN_SIZE, p[0]+MIN_SIZE, p[1]+MIN_SIZE)
        hits = idx.intersection(pbox, objects='raw')
        d = INFTY
        s = None
        for h in hits:
            nearest_p, new_d = get_distance(p, h[1])
            if d >= new_d:
                d = new_d
                s = (h[0], h[1], nearest_p, new_d)
        result[p] = s
        print s

        #some checking you could remove after you adjust the constants
        if s == None:
            raise Exception("It seems INFTY is not big enough.")

        pboxpol = ( (pbox[0], pbox[1]), (pbox[2], pbox[1]),
                    (pbox[2], pbox[3]), (pbox[0], pbox[3]) )
        if not Polygon(pboxpol).intersects(LineString(s[1])):
            msg = "It seems MIN_SIZE is not big enough. "
            msg += "You could get inexact solutions if remove this exception."
            raise Exception(msg)


def get_rtree(lines):
	def generate_items():
		sindx = 0
		for lid, l in lines:
			for i in xrange(len(l)-1):
				a, b = l[i]
				c, d = l[i+1]
				segment = ((a,b), (c,d))
				box = (min(a, c), min(b,d), max(a, c), max(b,d))
				#box = left, bottom, right, top
				yield (sindx, box, (lid, segment))
				sindx += 1
	return index.Index(generate_items())