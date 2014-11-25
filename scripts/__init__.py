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
    from app.models import Station

    importer = Importer(host, path)
    data = []
    for station in importer.do_import(limit):
        lonlat = 'POINT(%f %f)' % (station.longitude, station.latitude)
        s = Station(name=station.name, geom=lonlat)
        data.append((station,s))

        print("%s: %d" % (station.name, len(station.measurements)))

    for raw,obj in data:
        #for m in s0.measurements:
        #    s1.append(Measurement())
        if len(raw.region) > 0:
            points = map(lambda x: ' '.join((str(i) for i in x)), raw.region)
            obj.region = 'POLYGON((%s))' % ','.join(points)
            db.session.add(obj)
            db.session.commit()

