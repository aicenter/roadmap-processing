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


        self.cities_envelopes = properties.get("cities_envelopes")
        pass

config: RoadmaptoolsConfig = fconfig.configuration.load((RoadmaptoolsConfig, None))


