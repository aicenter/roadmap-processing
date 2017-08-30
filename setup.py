from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements("requirements.txt")

reqs = [str(ir.req) for ir in install_reqs]

setup(
   name='roadmap-processing',
   version='0.1',
   description='OSM and geoJSON tools',
   author='Martin Korytak',
   author_email='cbudrud@gmail.com',
   packages=['roadmap-processing'],
   url = 'https://github.com/peterldowns/mypackage', # change this
   download_url = 'https://github.com/peterldowns/mypackage/archive/0.1.tar.gz', # change this
   install_requires=reqs,
)
