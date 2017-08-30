from setuptools import setup
#from pip.req import parse_requirements

#install_reqs = parse_requirements("requirements.txt",session='hack')

#reqs = [str(ir.req) for ir in install_reqs]

setup(
   name='roadmaptools',
   version='0.1.1',
   description='OSM and geoJSON tools',
   author='Martin Korytak',
   author_email='cbudrud@gmail.com',
   packages=['roadmaptools'],
   url = 'https://github.com/aicenter/roadmap-processing',
   download_url = 'https://github.com/aicenter/roadmap-processing/archive/0.1.1.tar.gz',
   install_requires=['osmread','setuptools','networkx','geojson','pip'],
)
