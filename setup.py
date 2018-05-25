from setuptools import setup

setup(
   name='roadmaptools',
   version='0.3',
   description='OSM and geoJSON tools',
   author='Martin Korytak',
   author_email='cbudrud@gmail.com',
   license='MIT',
   packages=['roadmaptools'],
   url = 'https://github.com/aicenter/roadmap-processing',
   download_url = 'https://github.com/aicenter/roadmap-processing/archive/0.2.5.tar.gz',
   install_requires=['osmread==0.2','setuptools', 'geojson==1.3.5','shapely>=1.6.4.post1', 'networkx==2.1',
                     'numpy==1.14.3', 'matplotlib==2.2.2', 'pandas==0.22.0', 'pip'],
)
