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

import geojson
import googlemaps
from datetime import datetime
import networkx as nx
import codecs
import os.path

from typing import Union, Tuple, List
from roadmaptools.printer import print_info


class GMapsAPI:  # GET ALL DATA FOR ALL TRAFFIC MODELS

	traffic_models = ["best_guess", "pessimistic", "optimistic"]
	temp_dict = dict()
	json_dict = dict()
	g = nx.DiGraph()

	max_paths_in_request = 10

	def __init__(self, pathname=None):
		self.pathname = pathname

	def find_edge(self, id, model):
		duration = self.temp_dict[id]['duration_' + model]
		distance = self.temp_dict[id]['distance_' + model]
		speed = self.temp_dict[id]['speed_' + model]
		return [duration, distance, speed]

	def google_maps_find_path(self, start: Tuple[float, float], target: Tuple[float, float], time: datetime,
							  model: str= "best_guess"):
		try:
			gmaps = googlemaps.Client(key='AIzaSyDoCeLZhFJkx2JTLH8UMcsouaVUIwbV_wY')
			# time = datetime(2017, 11, 14, 7, 0, 0)  # 7 hours after midnight
			# print_info("Request sent")
			result = gmaps.directions(start, target, mode="driving", language="en-GB", units="metric",
										   departure_time=time, traffic_model=model)
			# print_info("Response obtained")
			# print(self.get_velocity(result))
			# duration = result['rows'][0]['elements'][0]['duration_in_traffic']['value']
			# distance = result['rows'][0]['elements'][0]['distance']['value']
			return result
		except (googlemaps.exceptions) as error:
			print_info("Google maps exception: {}".format(error))

	def get_durations_and_distances(self, starts: Union[Tuple[float, float], List[Tuple[float, float]]],
									targets: Union[Tuple[float,float], List[Tuple[float,float]]], time: datetime,
									model: str= "best_guess"):
		rows = []
		for index, start in enumerate(starts):
			start_batch, target_batch = 0
			if index % self.max_paths_in_request == 0:
				if index > 0:
					result = self.google_maps_find_path(start_batch, target_batch, time, model)
					rows.extend(result['rows'])
				start_batch = []
				target_batch = []

			start_batch.append(start)
			target_batch.append(targets[index])

		durations = []
		distances = []
		for row in rows:
			durations.append(row['elements'][0]['duration_in_traffic']['value'])
			distances.append(row['elements'][0]['distance']['value'])

		return durations, distances


	def get_node(self, node):
		return (node[1], node[0])  # order is latlon

	def get_velocity(self, gmaps_result):  # now works with optimistic time
		print(gmaps_result)
		try:
			time = gmaps_result['rows'][0]['elements'][0]['duration_in_traffic'][
				'value']  # gmaps_result['rows'][0]['elements'][0]['duration']['value']
			distance = gmaps_result['rows'][0]['elements'][0]['distance']['value']
			velocity = distance / time
			return '{} {}'.format(velocity * 3.6, 'km/h')
		except ZeroDivisionError:
			print("DIVISION BY ZERO!!!")

	def load_file_and_graph(self):
		with codecs.open(self.pathname + ".geojson", encoding='utf8') as f:
			self.json_dict = geojson.load(f)

		if os.path.exists("temp_data.gpickle"):
			self.g = nx.read_gpickle("temp_data.gpickle")
		else:
			for item in self.json_dict['features']:
				coord = item['geometry']['coordinates']
				coord_u = self.get_node(coord[0])
				coord_v = self.get_node(coord[-1])
				self.g.add_edge(coord_u, coord_v, id=item['properties']['id'])

			f.close()

	def get_gmaps_data(self):
		for n, nbrsdict in self.g.adjacency_iter():
			for nbr, keydict in nbrsdict.items():
				for key, d in keydict.items():
					if 'duration_optimistic' not in d:
						for model in self.traffic_models:
							res = self.google_maps_find_path(n, nbr, model)  # return duration, distance, speed
							d['duration_' + model] = res[0]
							d['distance_' + model] = res[1]
							d['speed_' + model] = res[2]

		nx.write_gpickle(self.g, "temp_data.gpickle")  # save for sure

		for n, nbrsdict in self.g.adjacency_iter():
			for nbr, keydict in nbrsdict.items():
				for key, d in keydict.items():
					self.temp_dict[d['id']] = {}
					for model in self.traffic_models:
						self.temp_dict[d['id']]['duration_' + model] = d['duration_' + model]
						self.temp_dict[d['id']]['distance_' + model] = d['distance_' + model]
						self.temp_dict[d['id']]['speed_' + model] = d['speed_' + model]

		for item in self.json_dict['features']:
			for model in self.traffic_models:
				res = self.find_edge(item['properties']['id'], model)  # return duration, distance, speed
				item['properties']['duration_' + model] = res[0]
				item['properties']['distance_' + model] = res[1]
				item['properties']['speed_' + model] = res[2]

	def save_file_to_geojson(self):
		with open(self.pathname + "-out.geojson", 'w') as outfile:
			geojson.dump(self.json_dict, outfile, indent=4, sort_keys=True)
		outfile.close()


# EXAMPLE
# test = Data_from_gmaps("prague_simple")
# test.load_file_and_graph()
# test.get_gmaps_data()
# test.save_file_to_geojson()

# stahnout data
# osmosis
# prekonvertovat do geojson
# procistit
# ohodnotit
