from roadmaptools.geojson import make_directed
from roadmaptools.util import filter_dict
from geojson import FeatureCollection, Feature, LineString

def test_make_directed():

    gj = FeatureCollection([
        Feature(id=1, geometry=LineString([[50, 10], [51, 0]]), properties={'highway': 'secondary'})
    ])

    gj_dir = make_directed(gj)
    assert len(gj_dir['features']) == 2

    gj = FeatureCollection([
        Feature(id=1, geometry=LineString([[50, 10], [51, 0]]), properties={'highway': 'secondary', 'oneway' : 'yes'})
    ])

    gj_dir = make_directed(gj)
    assert gj_dir == gj




if __name__ == '__main__':
    test_make_directed()