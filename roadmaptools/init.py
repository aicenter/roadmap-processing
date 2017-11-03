import fconfig.configuration as configuration

from typing import TypeVar
from typing import Type
from fconfig.config import Config
from roadmaptools.config.roadmaptools_config import RoadmaptoolsConfig

C = TypeVar('C', bound=Config)
CC = TypeVar('CC', bound=Config)

config = RoadmaptoolsConfig()


def load_config(client_config_type: Type[Config], key_in_client: str, client_local_config: str=None):
	global config
	client_config, config \
		= configuration.load(RoadmaptoolsConfig, client_config_type, client_local_config, key_in_client)
	return client_config, config