import fconfig.configuration as configuration

from typing import TypeVar
from typing import Type
from fconfig.config import Config
from roadmaptools.config.roadmaptools_config import RoadmaptoolsConfig
import roadmaptools
config = roadmaptools.config.roadmaptools_config.config
# C = TypeVar('C', bound=Config)
# CC = TypeVar('CC', bound=Config)
#
# config = RoadmaptoolsConfig()
#
#
# def load_config(client_config: CC, key_in_client: str, client_local_config: str = None,
#                 client_config_file_path: str=None):
#     configuration.load(config, client_config, client_config_file_path, client_local_config, key_in_client)
#     return config

