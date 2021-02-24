#
# Copyright (c) 2021 Czech Technical University in Prague.
#
# This file is part of Roadmaptools 
# (see https://github.com/aicenter/roadmap-processing).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
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

