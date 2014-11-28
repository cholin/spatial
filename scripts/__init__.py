from manage import manager
from app.exts import db

@manager.command
def resetdb():
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
    import json
    from scripts.importer.importer import Importer
    from app.models import Station, Measurement

    importer = Importer(host, path)
    for station in importer.do_import(limit):
        geom = station.coords.wkt if station.coords is not None else None
        region = station.region.wkt if station.region is not None else None
        obj = Station(name=station.name, altitude=station.altitude, geom=geom, region=region)
        for m in station.measurements:
            o = Measurement(type='temperature',value=m.temperature,date=m.date)
            obj.measurements.append(o)
        db.session.add(obj)
        db.session.commit()

        print("%s: %d" % (station.name, len(station.measurements)))
