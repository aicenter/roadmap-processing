from roadmaptools.osm import osm_to_geojson, DEFAULT_KEEP_TAGS
from roadmaptools.geojson import save_geojson, extract_road_network, make_directed, simplify_features, sanitize_geojson_properties
from roadmaptools.graph import geojson_to_nxgraph, simplify_graph, plot_graph
import matplotlib.pyplot as plt
import networkx as nx

if __name__ == '__main__':
    gj = osm_to_geojson('test_data/techobuz.osm', keep_tags=DEFAULT_KEEP_TAGS)
    save_geojson(gj, 'test_data/techobuz.geojson')
    gj = sanitize_geojson_properties(gj)
    gj = extract_road_network(gj)
    save_geojson(gj, 'test_data/techobuz_directed.geojson')
    nx_graph = geojson_to_nxgraph(gj)

    plt.figure()
    nx.draw_networkx(nx_graph, with_labels=False, pos=dict([(n, n) for n in nx_graph.nodes]))
    plt.show()

    simplify_graph(nx_graph)
    plt.figure()
    nx.draw_networkx(nx_graph, with_labels=False, pos=dict([(n, n) for n in nx_graph.nodes]))
    plt.show()

    nx_graph = nx.convert_node_labels_to_integers(nx_graph, label_attribute='pos', first_label=1)

    plt.figure()
    nx.draw_networkx(nx_graph, nx.get_node_attributes(nx_graph, 'pos'))
    plt.show()