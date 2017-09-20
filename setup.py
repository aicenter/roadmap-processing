from setuptools import setup

setup(
   name='roadmaptools',
   version='0.2.4.7',
   description='OSM and geoJSON tools',
   author='Martin Korytak',
   author_email='cbudrud@gmail.com',
   license='MIT',
   packages=['roadmaptools'],
   url = 'https://github.com/aicenter/roadmap-processing',
   download_url = 'https://github.com/aicenter/roadmap-processing/archive/0.2.4.7.tar.gz',
   install_requires=['osmread==0.2','setuptools','networkx==1.11','geojson==1.3.5','pip'],
)
