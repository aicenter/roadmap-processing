
from fconfig.config import Config



class RoadmaptoolsConfig(Config):

    def __init__(self):
        self.map_dir = None
        self.osm_source_url = None
        self.osm_map_filename = None
        self.filtered_osm_filename = None
        self.geojson_file = None
        self.cleaned_geojson_file = None
        self.sanitized_geojson_file = None
        self.simplified_file = None
        self.simplified_file_with_speed = None
        self.simplified_file_with_speed_and_curvature = None
        self.utm_center_lon = None
        self.utm_center_lat = None
        self.shift_utm_coordinate_origin_to_utm_center = None
        self.shapely_error_tolerance = None



        pass

    def fill(self, properties: dict=None):
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
        self.utm_center_lon = properties.get("utm_center_lon")
        self.utm_center_lat = properties.get("utm_center_lat")
        self.shift_utm_coordinate_origin_to_utm_center = properties.get("shift_utm_coordinate_origin_to_utm_center")
        self.shapely_error_tolerance = properties.get("shapely_error_tolerance")



        pass

