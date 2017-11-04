
from fconfig.config import Config


class RoadmaptoolsConfig(Config):

    def __init__(self):
        self.osm_source_url = None
        self.osm_map_filename = None
        self.filtered_osm_filename = None



        pass

    def fill(self, properties: dict=None):
        self.osm_source_url = properties.get("osm_source_url")
        self.osm_map_filename = properties.get("osm_map_filename")
        self.filtered_osm_filename = properties.get("filtered_osm_filename")



        pass

