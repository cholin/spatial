import json
from geoalchemy2 import Geometry, functions as func
from .exts import db

class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    altitude = db.Column(db.Integer)
    geom = db.Column(Geometry('POINT'))
    region = db.Column(Geometry())
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
    type = db.Column(db.String)
    value = db.Column(db.Float)
    date = db.Column(db.DateTime)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))

    def to_geojson(self):
        return {
            "type": "Feature",
            "properties": {
                "name": self.station.name,
                "type": self.type,
                "value": self.value
            },
            "geometry" : self.station.region_as_geojson()
        }
