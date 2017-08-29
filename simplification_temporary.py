from geojson import Point, LineString, Feature
import networkx as nx
import codecs
from simplify_graph import load_file, prepare_to_saving_optimized, save_file_to_geojson, simplify_graph


##udelat komponenty a detekce vice hran mezi 2 nody

def traverse_and_create_graph(g, subgraph):
    temp_g = nx.MultiDiGraph()
    for n, nbrsdict in g.adjacency_iter():
        if n in subgraph:
            for nbr, keydict in nbrsdict.items():
                if nbr in subgraph:
                    for key, d in keydict.items():
                        temp_g.add_edge(n, nbr, id=d['id'], others=d['others'], lanes=d['lanes'])
    return temp_g

def find_max_id(json_dict):
    max_id = -1
    for item in json_dict['features']:
        #print item['properties']['id']
        if item['properties']['id'] > max_id:
            max_id = item['properties']['id']
    return max_id

def get_node(node):
    return (node[1], node[0])  # order latlon


def detect_parallel_edges(g):
    for n, nbrsdict in g.adjacency_iter():
        for nbr, keydict in nbrsdict.items():
            for key, d in keydict.items():
                if key != 0:
                    temp_edges.append((g[n][nbr][key], get_node_reversed(n), get_node_reversed(nbr)))
                    g.remove_edge(n, nbr, key)


def get_node_reversed(node):
    return [node[1], node[0]]


def add_new_edges(json_dict, edge, new_id):
    # print ""
    # print edge
    for item in json_dict['features']:
        if item!={} and edge[0]['id'] == item['properties']['id']:
            print "yes"
            line_string1 = LineString(coordinates=(edge[1], edge[0]['others'][0]))
            edge[0]['others'].append(edge[2])
            line_string2 = LineString(coordinates=edge[0]['others'][1:])

            feature2 = Feature(geometry=line_string2, id=new_id, properties=item['properties'])
            feature1 = Feature(geometry=line_string1, id=item['properties']['id'], properties=item['properties'])
            print new_id
            print feature1, feature2
            temp_features.append(feature1)
            temp_features.append(feature2)
            item.clear()
            break


def load_graph(json_dict):
    g = nx.MultiDiGraph()
    for item in json_dict['features']:
        coord = item['geometry']['coordinates']
        coord_u = get_node(coord[0])
        coord_v = get_node(coord[-1])
        if coord_u != coord_v or len(coord) != 2:  # prune loops without any purpose, save loops like traffic roundabout
            lanes = item['properties']['lanes']
            data = item['geometry']['coordinates'][1:-1]
            if len(data) == 0:
                data = [[]]
            g.add_edge(coord_u, coord_v, id=item['properties']['id'], others=data, lanes=lanes)
    return g


temp_edges = list()
f = codecs.open("data/output-result.geojson", 'r')
json_dict = load_file(f)
f.close()
# for item in json_dict['features']:
#     print item

graph = load_graph(json_dict)
biggest_subgraph = set()
print "before:", len(graph.edges())
if not nx.is_strongly_connected(graph):
    maximum_number_of_nodes = -1
    for subgraph in nx.strongly_connected_components(graph):
        if len(subgraph) > maximum_number_of_nodes:
            maximum_number_of_nodes = len(subgraph)
            biggest_subgraph = subgraph

            # print maximum_number_of_nodes,biggest_subgraph

new_graph = traverse_and_create_graph(graph, biggest_subgraph)
print "after:", len(new_graph.edges())

# print "after:", len(new_graph.edges())
simplify_graph(new_graph, False)
detect_parallel_edges(new_graph)


temp_features = list()

id_iter = find_max_id(json_dict) + 1 # new id iterator
print id_iter

# for edge in temp_edges:
#     add_new_edges(json_dict, edge, id_iter)
#     id_iter += 1

#json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
prepare_to_saving_optimized(new_graph, json_dict)
# for item in json_dict['features']:
#     print item




# print temp_edges
# print len(temp_edges)
json_dict['features'] = [i for i in json_dict["features"] if i]  # remove empty dicts
#
#json_dict['features'] = json_dict['features'] + temp_features
#
# for item in json_dict['features']:
#     print item

#nefunguje :(((((((((((((((((((((((

f = open("data/output-test.geojson", 'w')
save_file_to_geojson(json_dict, f)
f.close()