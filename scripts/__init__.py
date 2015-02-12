from manage import manager

@manager.command
def resetdb():
    """
        Drops all tables in our database, installs postgis extension if
        necessary and recreates all tables
    """
    from app.exts import db

    # drop all tables
    db.drop_all()

    # install postgis if not already done
    sql = "SELECT count(extname) FROM pg_extension WHERE extname = 'postgis'"
    if (db.engine.execute(sql).rowcount == 0): db.engine.execute("CREATE EXTENSION postgis;")

    # create all tables
    db.create_all()


DEFAULT_HOST = 'ftp.dwd.de'
DEFAULT_PATH= 'pub/CDC/observations_germany/climate//hourly/air_temperature/recent/'
@manager.command
@manager.option('-h', '--host', help='host')
@manager.option('-p', '--path', help='path')
@manager.option('-l', '--limit', help='limit (maximum of imported stations)')
def import_weather(host = DEFAULT_HOST, path = DEFAULT_PATH, limit = None):
    """
        Imports weather data from 'Deutscher Wetter Dienst' into our database.
    """
    import json
    from app.exts import db
    from scripts.dwd.importer import Importer
    from app.models import Station, Measurement
    from geoalchemy2.elements import WKTElement
    from geoalchemy2.shape import to_shape, from_shape

    importer = Importer(host, path)
    print("Importing from %s (%s)\n" % (host, path))

    # import stations and measurements
    for i,(station,measurements) in enumerate(importer.do_import()):
        if limit is not None and i+1 > int(limit):
            break

        if len(measurements) > 0:
            geom = from_shape(station.coords, srid=4326)
            obj = Station(name=station.name, altitude=station.altitude, geom=geom)
            for m in measurements:
                # only add measurements for 00:00, 06:00, 12:00, 18:00, 24:00
                if m.date.hour % 6 == 0:
                    o = Measurement(type='temperature',value=m.temperature,date=m.date)
                    obj.measurements.append(o)

            db.session.add(obj)
            db.session.commit()

            print("\t%d. %s: %d" % (i+1, obj.name, len(obj.measurements)))

    # Calculate regions for stations (voronoi)
    stations = Station.query.all()
    points = [to_shape(s.geom) for s in stations]
    for i,region in Importer.generate_regions(points):
        if region is not None:
            stations[i].region = from_shape(region, srid=4326)
            db.session.add(stations[i])

    db.session.commit()


@manager.command
def import_forecast(date_from, date_to = None):
    """
        Downloads forecasts from noaa.gov (offered as grib2 files through a perl
        web service) and imports them as raster.
    """
    import sys
    from scripts.noaa_gfs.importer import forecast_noaa_import
    from app.exts import db
    from datetime import timedelta
    from app.models import Forecast

    print("Downloading and importing data from noaa gfs:")

    imported = []
    errors = []
    table = Forecast.__table__.name
    intervals = [24, 48]
    generator = forecast_noaa_import(date_from, date_to, table, intervals)
    for date, interval, sql in generator:
        if sql is not None:
            # create new record with output of raster2sql
            db.engine.execute(sql)

            # set date and interval for previously created record
            obj = Forecast.query.order_by('-rid').first()
            obj.date = date
            obj.interval = timedelta(hours=interval)
            db.session.add(obj)
            db.session.commit()

            imported.append(obj)

            print("."),
        else:
            errors.append((date,interval))
            print("*"),
        sys.stdout.flush()

    print("\n\nImported %d rasters (%d errors)" % (len(imported), len(errors)))

    print("\nErrors:")
    for d,i in errors:
        print("\t* %s %d - file not found" % (d.strftime("%Y-%m-%d %H:%M"), i))


@manager.command
@manager.option('-p', '--driver_path', help='path to your jdbc3 postresql jar')
def schema_spy(schema_spy_path, driver_path = None):
    import shutil
    from flask import current_app
    from subprocess import call

    _, _, uri, db = current_app.config['SQLALCHEMY_DATABASE_URI'].split('/')
    cred, host = uri.split('@')
    user, pw = cred.split(':')
    dest = 'doc/tables'

    cmd = ['java', '-jar',
           schema_spy_path,
           '-t', 'pgsql',
           '-db', db,
           '-host', host,
           '-s', 'public',
           '-u', user,
           '-p', pw,
           '-o', dest
    ]

    if driver_path is not None:
        cmd.extend(['-dp', driver_path])

    shutil.rmtree(dest)
    call(cmd)
