import copy

import geojson
from geojson import Point, LineString, Feature, FeatureCollection
from tqdm import tqdm
import shapely.geometry
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def geojson_to_nxgraph(json_dict: dict) -> nx.MultiDiGraph:
    g = nx.MultiDiGraph()
    for item in json_dict['features']:
        coord = item['geometry']['coordinates']
        coord_u = (coord[0][1], coord[0][0])  # lat lon, first node
        coord_v = (coord[-1][1], coord[-1][0])  # lat lon, last node
        if coord_u != coord_v or len(coord) != 2:  # prune loops without any purpose, save loops like traffic roundabout
            lanes = item['properties']['lanes']
            g.add_edge(coord_u, coord_v, id=item['properties']['id'], others=[[]], lanes=lanes)
    return g


def simplify_oneways(n, g, check_lanes):
    edge_u = list(g.out_edges(n, data=True))[0][:2]
    temp = reversed(edge_u)
    edge_u = tuple(temp)
    edge_v = list(g.in_edges(n, data=True))[0][:2]
    new_id = list(g.out_edges(n, data=True))[0][2]['id']
    coords = list(filter(None, list(g.in_edges(n, data=True))[0][2]['others'] + [[n[1], n[0]]]
                         + list(g.out_edges(n, data=True))[0][2]['others']))
    lanes_u = list(g.out_edges(n, data=True))[0][2]['lanes']
    lanes_v = list(g.in_edges(n, data=True))[0][2]['lanes']
    if edge_u != edge_v:
        # remove edges and node
        if lanes_u == lanes_v or lanes_u is None or lanes_v is None or check_lanes:  # merge only edges with same number of lanes
            g.add_edge(edge_v[0], edge_u[0], id=new_id, others=coords, lanes=lanes_u)
            g.remove_edge(edge_u[1], edge_u[0])
            g.remove_edge(edge_v[0], edge_v[1])
            g.remove_node(n)
    elif edge_u == edge_v and hash_list_of_lists_and_compare(list(g.in_edges(n, data=True))[0][2]['others'],
                                                             list(g.out_edges(n, data=True))[0][2]['others']):
        if lanes_u == lanes_v or lanes_u is None or lanes_v is None or check_lanes:  # merge only edges with same number of lanes
            g.add_edge(edge_v[0], edge_u[0], id=new_id, others=coords, lanes=lanes_u)
            g.remove_edge(edge_u[1], edge_u[0])
            g.remove_edge(edge_v[0], edge_v[1])
            g.remove_node(n)


def hash_list_of_lists_and_compare(list1, list2):
    temp_hash1 = [tuple(i) for i in list1]
    temp_hash2 = [tuple(i) for i in list2]
    return set(temp_hash1) != set(temp_hash2)


def check_oneway_loop(edge):
    return edge[0] == edge[1]


def simplify_twoways(n, g, check_lanes):
    edge_u1 = list(g.out_edges(n, data=True))[0][:2]
    edge_u2 = list(g.out_edges(n, data=True))[1][:2]
    temp1 = reversed(edge_u1)
    edge_u1 = tuple(temp1)
    temp2 = reversed(edge_u2)
    edge_u2 = tuple(temp2)
    new_id_out = list(g.out_edges(n, data=True))[0][2]['id']
    new_id_in = list(g.in_edges(n, data=True))[0][2]['id']
    coords_out = list(filter(None, list(g.in_edges(n, data=True))[1][2]['others'] + [[n[1], n[0]]]
                             + list(g.out_edges(n, data=True))[0][2]['others']))
    coords_in = list(reversed(coords_out))
    edge_v1 = list(g.in_edges(n, data=True))[0][:2]
    edge_v2 = list(g.in_edges(n, data=True))[1][:2]
    edges_u = (edge_u1, edge_u2)
    edges_v = (edge_v1, edge_v2)
    lanes_u1 = list(g.out_edges(n, data=True))[0][2]['lanes']
    lanes_u2 = list(g.out_edges(n, data=True))[1][2]['lanes']
    lanes_v1 = list(g.in_edges(n, data=True))[0][2]['lanes']
    lanes_v2 = list(g.in_edges(n, data=True))[1][2]['lanes']
    if edges_u == edges_v:

        # remove edges and node
        is_deleted = [False, False]
        is_loop = False  # finding oneway loop (from_id == to_id)

        for i in edges_u:
            if check_oneway_loop(i):
                is_loop = True

        for i in edges_v:
            if check_oneway_loop(i):
                is_loop = True

        if is_loop:
            return

        if lanes_u1 == lanes_v2 or lanes_u1 is None or lanes_v2 is None or check_lanes:  # merge only edges with same number of lanes
            g.remove_edge(edge_u1[1], edge_u1[0])
            g.remove_edge(edge_u2[0], edge_u2[1])
            g.add_edge(edge_v2[0], edge_v1[0], id=new_id_out, others=coords_out, lanes=lanes_u1)
            is_deleted[0] = True

        if lanes_u2 == lanes_v1 or lanes_u2 == None or lanes_v1 == None or check_lanes:  # merge only edges with same number of lanes
            if edge_u1[1] != edge_u1[0] or edge_u2[0] != edge_u2[1]:  # check  loops
                g.remove_edge(edge_u1[0], edge_u1[1])
                g.remove_edge(edge_u2[1], edge_u2[0])
                g.add_edge(edge_v1[0], edge_v2[0], id=new_id_in, others=coords_in, lanes=lanes_v1)
                is_deleted[1] = True

        if is_deleted[0] == True and is_deleted[1] == True or check_lanes:
            g.remove_node(n)


def simplify_graph(g: nx.MultiDiGraph, check_lanes=True):
    for n, _ in list(g.adjacency()):
        if g.out_degree(n) == 1 and g.in_degree(n) == 1:  # oneways
            simplify_oneways(n, g, check_lanes)

    for n, _ in list(g.adjacency()):
        if g.out_degree(n) == 2 and g.in_degree(n) == 2:  # both directions in highway
            simplify_twoways(n, g, check_lanes)


def plot_graph(gr):
    plt.figure()
    nx.draw_networkx(gr, nx.get_node_attributes(gr, 'pos'))
    plt.show()


def show_graph(graph):

    # plot the graph
    nlat = nx.get_node_attributes(graph, 'lat').values()
    nlon = nx.get_node_attributes(graph, 'lon').values()

    plt.axis('equal')
    plt.scatter(nlon, nlat, marker='.')

    lats = []
    lons = []

    for s, d, k in graph.edges(keys=True):
        slat = graph.nodes[s]['lat']
        slon = graph.nodes[s]['lon']
        dlat = graph.nodes[d]['lat']
        dlon = graph.nodes[d]['lon']

        lats.append(slat)
        lats.append(dlat)
        lats.append(None)

        lons.append(slon)
        lons.append(dlon)
        lons.append(None)

    plt.plot(lons, lats, 'b-')


    # plot travel time
    # traveltimes_to_print = 10000
    # print('Plotting travel time for first %d edges to check for sanity.' % traveltimes_to_print)
    # i = 0
    # for s, d in graph.edges:
    #     spos = np.array([graph.nodes[s]['lon'], graph.nodes[s]['lat']])
    #     dpos = np.array([graph.nodes[d]['lon'], graph.nodes[d]['lat']])
    #
    #     mid = spos + (dpos - spos) * 0.55
    #     plt.text(mid[0], mid[1], "%d" % (graph[s][d]['weight']))
    #
    #     if i >= traveltimes_to_print:
    #         break
    #     i += 1

    plt.show()
