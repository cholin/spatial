Importer for DWD observations
=============================

The [german weather service](http://www.dwd.de) provides a daily observation of
weather in Germany. You can download this data from the following url:

  <ftp://ftp.dwd.de/pub/CDC/observations_germany/climate/daily/kl/>

To be able to import weather data by stations this import script can be useful.
To import data just do the following:

```
$ git clone git@github.com:cholin/spatial.git
$ cd spatial/scripts
$ python2 -m importer
```

You can limit the imported data with argument `-l <number>`. The imported data
will be saved as a json file (`weather.json`) in the current working dir.

Implementation details
----------------------

The importer downloads the station summary file to get a list of all weather
stations. After that it downloads for each station the corresponding zip file
(with measurement data), extracts it in-memory and parses it. To get
information about which weather station is the nearest for a given point, it
also calculates a region polygon for each station. This is done by computing the
voronoi diagram for all stations. The resulting regions may be outside of the
country germany. To avoid this there is a polygon of the border of germany
(data is from
[naturalearthdata.com](http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip) - country extraction and
exportation as geojson with qgis). For each region we calculate the
intersection with this polygon and use the result as final region
(Multi)Polygon.
