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

import roadmaptools.inout

from roadmaptools.printer import print_info
from roadmaptools.init import config

print_info("Loading start")
#oadmaptools.inout.load_gpx("/home/fido/AIC data/Shared/EXPERIMENTAL/traces/traces-raw.gpx")
roadmaptools.inout.load_gpx('/home/olga/Documents/GPX/test1.gpx')
print_info("Loading end")