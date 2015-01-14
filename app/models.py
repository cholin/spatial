import json
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

    def region_as_geojson(self):
        region = None
        if self.region is not None:
            region =  json.loads(db.session.scalar(func.ST_AsGeoJSON(self.region)))
        return region

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, index=True)
    value = db.Column(db.Float)
    date = db.Column(db.DateTime, index=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))

    @classmethod
    def all(cls, mtype, date = None):
        qry = db.session.query(cls).filter(cls.type == mtype) \
                    .filter(cls.value != -999) \
                    .order_by(desc(cls.date))

        if date is None:
            date_cmp = qry.first().date
        else:
            date_cmp = datetime.strptime(date, "%Y-%m-%d")

        return date_cmp, qry.filter(Measurement.date == date_cmp).all()

    def to_geojson(self):
        return {
            "type": "Feature",
            "properties": {
                "name": self.station.name,
                "altitude": self.station.altitude,
                "type": self.type,
                "value": self.value
            },
            "geometry" : self.station.region_as_geojson()
        }


class Forecast(db.Model):
    rid = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, index=True)
    subtype = db.Column(db.String)
    date = db.Column(db.DateTime)
    interval = db.Column(db.Interval)
    rast = db.Column(Raster())

    @classmethod
    def get_raster_img(cls, ftype, date):
        result = db.engine.execute("""
            SELECT
                ST_AsPNG(
                    ST_Transform(
                        ST_CLIP(
                            ST_ColorMap(
                                ST_Resample(
                                    rast,
                                    800,
                                    800,
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
                            True
                        ),
                        3857
                    )
                ) as img
            FROM
                forecasts
            LIMIT 1
        """);
        return result.first()['img']
