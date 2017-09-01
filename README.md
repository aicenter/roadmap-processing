# roadmap-processing

Python's tool for processing mostly geoJSON files and also OSM files. 

### Prerequisites

We will work with [pip](https://pypi.python.org/pypi/pip), [wget](https://www.gnu.org/software/wget/) and [virtualenv](https://virtualenv.pypa.io/en/stable/)(optional). You can follow steps below to install it properly.

### Installing

Use

```
python get-pip.py
```

for installing pip and

```
sudo pip install virtualenv
```

for virtualenv or eventually on Windows use


```
pip install virtualenv
```

If you are running in Linux, type


```
mkdir ~/virtualEnvironment && cd ~/virtualEnvironment
```

then clone this GitHub project

```
git clone https://github.com/aicenter/roadmap-processing.git
```
or clone with ssh
```
git clone git@github.com:aicenter/roadmap-processing.git
```

and finally use

```
virtualenv --python path/to/python2.7/interpreter --no-site-packages --distribute .env && source .env/bin/activate
```

where you subtitute path/to/python2.7/interpreter with your own path to python 2.7 interpreter to create isolated Python environment.

This project is also available on PyPI and it is recommended install it as package

```
pip install roadmaptools
```

## Examples of usage

Almost in every script there are two ways how to run it or get resulting geoJSON.

####osmtogeojson

```python
   geojson_file = osmtogeojson.convert_osmtogeojson("path/to/OSMfile.osm")
   osmtogeojson.is_geojson_valid(geojson_file)
   f = open("path/to/savefile.geojson","w")
   osmtogeojson.save_geojson(geojson_file,f)
   f.close()
```

First of all, check your versions of required packages

```
python install_requirements.py
```

after that you can simply download your favourite city.

```
python mapdownloader.py "Barcelona"
```

You can skip this, if you have own city area and continue with

```
python run_demo.py map.osm -r
```
and your final result is in folder "/data" as "output-final-result.geojson".

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
