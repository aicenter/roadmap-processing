
import fconfig.configuration

from fconfig.config import Config

class RoadmaptoolsConfig(Config):
    def __init__(self, properties: dict=None):
        self.map_dir = properties.get("map_dir")
        self.osm_source_url = properties.get("osm_source_url")
        self.osm_map_filename = properties.get("osm_map_filename")
        self.filtered_osm_filename = properties.get("filtered_osm_filename")
        self.geojson_file = properties.get("geojson_file")
        self.cleaned_geojson_file = properties.get("cleaned_geojson_file")
        self.sanitized_geojson_file = properties.get("sanitized_geojson_file")
        self.simplified_file = properties.get("simplified_file")
        self.simplified_file_with_speed = properties.get("simplified_file_with_speed")
        self.simplified_file_with_speed_and_curvature = properties.get("simplified_file_with_speed_and_curvature")
        self.ap_nodes_file = properties.get("ap_nodes_file")
        self.ap_edges_file = properties.get("ap_edges_file")
        self.utm_center_lon = properties.get("utm_center_lon")
        self.utm_center_lat = properties.get("utm_center_lat")
        self.shift_utm_coordinate_origin_to_utm_center = properties.get("shift_utm_coordinate_origin_to_utm_center")
        self.shapely_error_tolerance = properties.get("shapely_error_tolerance")
        self.osm_filter_params = properties.get("osm_filter_params")


        pass

config: RoadmaptoolsConfig = fconfig.configuration.load((RoadmaptoolsConfig, None))


