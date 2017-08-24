import geojson
import networkx as nx
import codecs
from simplify_graph import load_file,load_graph,simplify_graph,prepare_to_saving_optimized,save_file_to_geojson

##udelat komponenty a detekce vice hran mezi 2 nody

def traverse_and_create_graph(g,subgraph):
    temp_g = nx.MultiDiGraph()
    for n, nbrsdict in g.adjacency_iter():
        if n in subgraph:
            for nbr, keydict in nbrsdict.items():
                if nbr in subgraph:
                    for key, d in keydict.items():
                        temp_g.add_edge(n,nbr,id=d['id'], others=[[]],lanes=d['lanes'])
    return temp_g

def detect_parallel_edges(g):
    unique_edges = set()
    for n, nbrsdict in g.adjacency_iter():
        for nbr, keydict in nbrsdict.items():
            if (n,nbr) in unique_edges:
                print "err"
            else:
                unique_edges.add((n, nbr))
              ##  print unique_edges
            for key, d in keydict.items():
                pass
                #print d

f = codecs.open("data/output-cleaned.geojson",'r')
json_dict = load_file(f)
f.close()
#print json_dict
graph = load_graph(json_dict)
print "before:", len(graph.edges())
if not nx.is_strongly_connected(graph):
    maximum_number_of_nodes = -1
    for subgraph in nx.strongly_connected_components(graph):
        if len(subgraph)>maximum_number_of_nodes:
            maximum_number_of_nodes = len(subgraph)
            biggest_subgraph = subgraph

   # print maximum_number_of_nodes,biggest_subgraph

new_graph = traverse_and_create_graph(graph,biggest_subgraph)
print "after:", len(new_graph.edges())
simplify_graph(new_graph, False)
#print "after:", len(new_graph.edges())
detect_parallel_edges(new_graph)

prepare_to_saving_optimized(new_graph, json_dict)

f = open("data/output-simple.geojson",'w')
save_file_to_geojson(json_dict, f)
f.close()
