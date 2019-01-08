import setuptools
from setuptools import setup

setup(
    name='roadmaptools',
    version='1.0.2',
    description='OSM and geoJSON tools',
    author='Martin Korytak',
    author_email='cbudrud@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    url = 'https://github.com/aicenter/roadmap-processing',
    download_url = 'https://github.com/aicenter/roadmap-processing/archive/0.2.5.tar.gz',
    install_requires=['osmread','setuptools','networkx>=2.0','geojson', 'gpx_lite', 'rtree', 'tqdm',
        'typing', 'numpy', 'fconfig', 'googlemaps', 'overpass', 'pandas', 'scipy', 'shapely'],
    python_requires='>=3',
    package_data={'roadmaptools.resources': ['*.cfg']}
)
