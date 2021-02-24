import setuptools
from setuptools import setup

setup(
    name='roadmaptools',
    version='4.1.0',
    description='Tools for road graph processing',
    author='David Fiedler, Martin Korytak',
    author_email='david.fiedler@agents.fel.cvut.cz',
    license='MIT',
    packages=setuptools.find_packages(),
    url = 'https://github.com/aicenter/roadmap-processing',
    # DO NOT remove the utm packege despite it is not detected by pipreqs
    install_requires=['fconfig', 'numpy', 'pandas', 'googlemaps', 'typing', 'gpx_lite', 'tqdm', 'overpass', 'shapely',
                      'setuptools', 'rtree', 'osmread', 'scipy', 'networkx>=2.0', 'geojson', 'utm'],
    python_requires='>=3',
    package_data={'roadmaptools.resources': ['*.cfg']}
)
