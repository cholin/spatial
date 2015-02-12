import json
import re
from datetime import datetime
from sqlalchemy import desc
from geoalchemy2 import Geometry, Raster, functions as func
from .exts import db

class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    altitude = db.Column(db.Integer)
    geom = db.Column(Geometry('POINT', srid=4326))
    region = db.Column(Geometry(srid=4326))
    measurements = db.relationship("Measurement", backref="station")

    def __repr__(self):
        return '<Station %r>' % self.name

    def as_geojson(self):
        regions = db.session.scalar(func.ST_AsGeoJSON(self.region)) or '{}'
        return json.loads(regions)

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, index=True)
    value = db.Column(db.Float)
    date = db.Column(db.DateTime, index=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))

    @classmethod
    def all(cls, mtype, mdate = None):
        qry = db.session.query(cls).filter(cls.type == mtype) \
                    .filter(cls.value != -999) \
                    .filter(Measurement.date == mdate) \
                    .order_by(desc(cls.date))

        return qry.all()

    def to_geojson(self):
        return {
            "type": "Feature",
            "properties": {
                "name": self.station.name,
                "altitude": self.station.altitude,
                "type": self.type,
                "value": self.value
            },
            "geometry" : self.station.as_geojson()
        }


class Forecast(db.Model):
    rid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    interval = db.Column(db.Interval)
    rast = db.Column(Raster())

    # which bands corresponds to which data?
    ftypes = {
        'temperature' : 0,
        'rainfall' : 1
    }

    def to_dict(self):
        return {
            'rid' : self.rid,
            'date' : self.date,
            'interval' : int(self.interval.total_seconds() // 3600)
        }

    @classmethod
    def get_forecasts_for_date(cls, ftype, date):
        qry = cls.query.filter((cls.date + cls.interval) == date)
        results = qry.all()
        return results

    @classmethod
    def get_meta(cls, ftype, date, interval):
        qry = "SELECT Box3d(rast) FROM forecast WHERE date + interval = '%s'" % date
        result = db.engine.execute(qry).first()
        pattern = r'BOX3D\(([\d\s.]*),([\d\s.]*)\)'
        points = re.search(pattern, result[0])
        top_left_x,top_left_y,_ = points.group(1).split(' ')
        bottom_right_x,bottom_right_y,_ = points.group(2).split(' ')

        return [(top_left_x, top_left_y), (bottom_right_x, bottom_right_y)]


    @classmethod
    def get_raster_img_for_rid(cls, ftype, rid):
        # TODO: sanitize user input!!
        result = db.engine.execute("""
            SELECT
                ST_AsPNG(
                    ST_Transform(
                        ST_CLIP(
                            ST_ColorMap(
                                ST_Resample(
                                    rast,
                                    1150,
                                    950,
                                    NULL,
                                    NULL,
                                    0,
                                    0,
                                    'Cubic'
                                ),
                                1,
                                'pseudocolor'
                            ),
                            (SELECT ST_UNION(region) FROM station),
                            false
                        ),
                        3857
                    )
                ) as img
            FROM
                forecast
            WHERE
                rid = '%s'
            LIMIT 1
        """ % rid);

        return result.first()['img']
