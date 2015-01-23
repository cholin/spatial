Spatial db project - weather data visualization
===============================================

Frameworks/Libraris used:

* Flask (web framework)
* SQLAlchemy+GeoAlchemy (postgres/postgis library)
* Numpy+Scipy (Math library)
* Shapely (Spatial library)
* Postgres+Postgis (relational database with spatial support)

How to get started
------------------

First you have to install postgres with postgis. Afterwards start it and create
a user and a database for our project:

```
$ sudo su postgres
$ createuser -D -P -s -R foo232
$ createdb -O foo232 foo23
```

Download the source, create a new virtualenv and install dependencies like
frameworks and libaries (you always need to activate your environment). It's
better if you install numpy via your distribution package manager:

```
$ git clone git@github.com:cholin/spatial.git
$ cd spatial
$ virtualenv2 env
$ . env/bin/activate               # activate virtual environment
$ pip install -r requirements.txt
```

Configure database credentials

```
$ cat config.cfg.dist > config.cfg
$ vim config.cfg                   # set credentials for SQLALCHEMY
```

Create database and import data from DWD (see [README](https://github.com/cholin/spatial/blob/master/scripts/importer/README.md))

```
$ python2 manage.py resetdb
$ python2 manage.py import_weather                # imports all recent dwd data
$ python2 manage.py import_forecast 2015-01-01    # import forecasts from
                                                  # 01.01.2015 until now
```

Start webserver

```
$ python2 manage.py runserver
$ firefox http://localhost:5000
```
