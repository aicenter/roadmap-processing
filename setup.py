import setuptools
from setuptools import setup

setup(
    name='roadmaptools',
    version='4.0.0',
    description='OSM and geoJSON tools',
    author='Martin Korytak',
    author_email='cbudrud@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    url = 'https://github.com/aicenter/roadmap-processing',
    download_url = 'https://github.com/aicenter/roadmap-processing/archive/0.2.5.tar.gz',
    # DO NOT remove the utm packege despite it is not detected by pipreqs
    install_requires=['fconfig', 'numpy', 'pandas', 'googlemaps', 'typing', 'gpx_lite', 'tqdm', 'overpass', 'shapely',
                      'setuptools', 'rtree', 'osmread', 'scipy', 'networkx>=2.0', 'geojson', 'utm'],
    python_requires='>=3',
    package_data={'roadmaptools.resources': ['*.cfg']}
)
