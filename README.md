# roadmap-processing

Python module for working with road network graphs, mostly from osm. Usefull tools for working with `geojson` and `gpx`
formats. 

## Prerequisites

We will work with Python [pip](https://pypi.python.org/pypi/pip). You should have all these installed before beginning 
 the installation.
<!-- and [virtualenv (optional)](https://virtualenv.pypa.io/en/stable/).  -->

## Installing

```
pip install roadmaptools
```

## Examples of usage
Download map from osm:

```Python
roadmaptools.download_map.download_cities(
    [(49.94, 14.22, 50.17, 14.71)], './raw_map.geojson')
```



## Versioning

We use [GitHub](https://github.com) for versioning. For the versions available, see the 
[tags on this repository](https://github.com/aicenter/roadmap-processing/tags). 

## Authors

* **David Fiedler** - *Maintainer*
* **Martin Korytak** - *Initial work*

See also the list of [contributors](https://github.com/aicenter/roadmap-processing/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details

