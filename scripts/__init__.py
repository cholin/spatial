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
DEFAULT_PATH= 'pub/CDC/observations_germany/climate/daily/kl/recent/'
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

    importer = Importer(host, path)
    for i,station in enumerate(importer.do_import(limit)):
        geom = None
        if station.coords is not None:
            geom = WKTElement(station.coords.wkt, srid=4326)

        region = None
        if station.region is not None:
            region = WKTElement(station.region.wkt, srid=4326)

        obj = Station(name=station.name, altitude=station.altitude, geom=geom, region=region)
        for m in station.measurements:
            o = Measurement(type='temperature',value=m.temperature,date=m.date)
            obj.measurements.append(o)

        db.session.add(obj)
        db.session.commit()

        print("\t%d %s: %d" % (i, station.name, len(station.measurements)))


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
    intervals = [24]
    generator = forecast_noaa_import(date_from, date_to, table, interals)
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
