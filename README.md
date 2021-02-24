<!--
Copyright (c) 2021 Czech Technical University in Prague.

This file is part of Roadmaptools 
(see https://github.com/aicenter/roadmap-processing).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
-->
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

