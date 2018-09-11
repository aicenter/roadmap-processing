from setuptools import setup

setup(
   name='roadmaptools',
   version='1.0.0',
   description='OSM and geoJSON tools',
   author='Martin Korytak',
   author_email='cbudrud@gmail.com',
   license='MIT',
   packages=['roadmaptools'],
   url = 'https://github.com/aicenter/roadmap-processing',
   download_url = 'https://github.com/aicenter/roadmap-processing/archive/0.2.5.tar.gz',
   install_requires=['osmread','setuptools','networkx','geojson','pip'],
)
