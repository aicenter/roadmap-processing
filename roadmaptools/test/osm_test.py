from roadmaptools.osm import osm_to_geojson, DEFAULT_KEEP_TAGS
from roadmaptools.geojson import save_geojson, extract_road_network, make_directed


def test_osm():
    gj = osm_to_geojson('test_data/techobuz.osm')
    assert len(gj['features']) == 145


if __name__ == '__main__':
    gj = osm_to_geojson('test_data/techobuz.osm', keep_tags=DEFAULT_KEEP_TAGS)
    save_geojson(gj, 'test_data/techobuz.geojson')
    gj_dir = make_directed(gj)
    save_geojson(gj_dir, 'test_data/techobuz_directed.geojson')
