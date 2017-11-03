
from fconfig.config import Config


class RoadmaptoolsConfig(Config):

    def __init__(self, properties: dict=None):
        super().__init__(properties)
        if properties:
            self.osm_source_url = properties.get("osm_source_url")
            self.osm_map_filename = properties.get("osm_map_filename")



