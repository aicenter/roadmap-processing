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
import roadmaptools.gpx

#trace_file = r"C:\AIC data\Shared\Map Matching Benchmark\2015 100 tracks dataset\00000000/trace-period-24.gpx"
trace_file = '/home/olga/Documents/GPX/test1.gpx'

gpx_content = roadmaptools.inout.load_gpx(trace_file)
print(gpx_content)
roadmaptools.gpx.cut_trace(gpx_content.tracks[0], 10)


#roadmaptools.inout.save_gpx(gpx_content, r"C:\AIC data\Shared\Map Matching Benchmark\test traces/trace_0-period_24-first_10_points.gpx")