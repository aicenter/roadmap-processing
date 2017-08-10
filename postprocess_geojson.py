import geojson
import codecs
from geojson import Point,Feature,FeatureCollection
import networkx as nx

class Postprocessing:

    g = nx.MultiDiGraph()

    def __init__(self,filename):
        self.filename = filename
        self.json_dict = {}

    def get_node(self,node):
        return (node[0], node[1])  # order lonlat

    def formated(self,check):
        self.is_formated = check

    def load_geojson_and_graph(self):
        print "loading file..."
        with codecs.open(self.filename, encoding='utf8') as f:
            self.json_dict = geojson.load(f)
        f.close()

        for item in self.json_dict['features']:
            coord = item['geometry']['coordinates']
            coord_u = self.get_node(coord[0])
            coord_v = self.get_node(coord[-1])
            self.g.add_edge(coord_u, coord_v, id=item['properties']['id'])

    def is_geojson_valid(self):
        validation = geojson.is_valid(self.json_dict)
        print "is geoJSON valid?", validation['valid']

    def export_points_to_geojson(self):
        print "exporting points..."
        list_of_features = []
        for n, _ in self.g.adjacency_iter():
            node_id = self.get_nodeID(str(n))
            point = Point(n)
            feature = Feature(geometry=point, properties={'node_id': node_id})
            list_of_features.append(feature)

        json_dict_with_points = FeatureCollection(features=list_of_features)

        with open('data/output-points.geojson', 'w') as outfile:
            geojson.dump(json_dict_with_points, outfile)
        outfile.close()

    def get_nodeID(self,node_id): #return String
        for char in [',', '.','[',']',' ', '(', ')']:
            if char in node_id:
                node_id = node_id.replace(char,'')
        return node_id #int(node_id)

    def postprocessing_file(self):
        print "processing..."
        for item in self.json_dict['features']:
            item['properties']['length'] = item['properties']['distance_best_guess']
            item['properties']['speed'] = item['properties']['speed_best_guess']
            del item['properties']['distance_best_guess']
            if 'distance_optimistic' in item['properties']:
                del item['properties']['distance_optimistic']
            if 'distance_pessimistic' in item['properties']:
                del item['properties']['distance_pessimistic']

            from_node = str(item['geometry']['coordinates'][0])
            to_node = str(item['geometry']['coordinates'][-1])
            from_nodeID = self.get_nodeID(from_node)
            to_nodeID = self.get_nodeID(to_node)
            item['properties']['from_id'] = from_nodeID
            item['properties']['to_id'] = to_nodeID

    def save_geojson(self):
        print "saving file..."
        with open('data/output-final-result.geojson', 'w') as outfile:
            if self.is_formated==False:
                geojson.dump(self.json_dict, outfile)
            else:
                geojson.dump(self.json_dict, outfile, indent=4, sort_keys=True)
        outfile.close()

#EXAMPLE OF USAGE
if __name__ == '__main__':
    test = Postprocessing("output-curvature.geojson")
    test.load_geojson_and_graph()
    test.is_geojson_valid()
    test.export_points_to_geojson()
    test.postprocessing_file()
    test.save_geojson()
