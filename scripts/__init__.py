from manage import manager
from app.exts import db
from geoalchemy2.elements import WKTElement

@manager.command
def resetdb():
    """
        Drops all tables in our database, installs postgis extension if
        necessary and recreates all tables
    """
    # drop all tables
    db.drop_all()

    # install postgis if not already done
    sql = "SELECT count(extname) FROM pg_extension WHERE extname = 'postgis'"
    if (db.engine.execute(sql).rowcount == 0):
      db.engine.execute("CREATE EXTENSION postgis;")

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
    from scripts.importer.importer import Importer
    from app.models import Station, Measurement

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
