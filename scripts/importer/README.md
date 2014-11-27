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
will be saved as an json file `weather.json` in the current working dir.
