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
import os

from typing import Callable
from tqdm import tqdm


def process_dir(dir_path: str, function: Callable[[str], None]):
	walk = list(os.walk(dir_path))[0]
	path = walk[0]
	files = walk[2]

	# # remove the link to parent dir
	# files = files[1:]
	for filename in tqdm(files, desc="Processing directory"):
		function(path + filename)