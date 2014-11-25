import json
from geoalchemy2 import Geometry, functions as func
from .exts import db

class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    altitude = db.Column(db.Integer)
    geom = db.Column(Geometry('POINT'))
    region = db.Column(Geometry('POLYGON'))
    measurements = db.relationship("Measurement", backref="station")

    def __repr__(self):
        return '<Station %r>' % self.name

    @property
    def geom_as_geojson(self):
      return {
        "type": "Feature",
        "properties": {"name": self.name},
        "geometry" : json.loads(db.session.scalar(func.ST_AsGeoJSON(self.geom)))
      }

    @property
    def region_as_geojson(self):
      return {
        "type": "Feature",
        "properties": {"name": self.name},
        "geometry" : json.loads(db.session.scalar(func.ST_AsGeoJSON(self.region)))
      }

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    value = db.Column(db.Float)
    date = db.Column(db.DateTime)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))
