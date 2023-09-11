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
import setuptools
from setuptools import setup

setup(
    name='roadmaptools',
    version='5.0.0',
    description='Tools for road graph processing',
    author='David Fiedler, Martin Korytak',
    author_email='david.fiedler@agents.fel.cvut.cz',
    license='MIT',
    packages=setuptools.find_packages(),
    url = 'https://github.com/aicenter/roadmap-processing',
    # DO NOT remove the utm packege despite it is not detected by pipreqs
    install_requires=[
        'fconfig',
        'numpy',
        'pandas',
        'googlemaps',
        'typing',
        'gpx_lite',
        'tqdm',
        'overpass',
        'shapely',
        'setuptools',
        'rtree',
        'scipy',
        'networkx>=2.0',
        'geojson',
        'utm'
    ],
    python_requires='>=3',
    package_data={'roadmaptools.resources': ['*.cfg']}
)
