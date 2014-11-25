# -*- coding: utf-8 -*-

from .utils import date_as_datetime

class Station:
    def __init__(self, identifier, name, altitude, latitude, longitude, date_start, date_end):
        self.identifier = int(identifier)
        self.name = name
        self.altitude = int(altitude)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.date_start = date_start
        self.date_end = date_end
        self.measurements = []
        self.region = []

    @property
    def lonlat(self):
        return (self.longitude, self.latitude)

    def to_dict(self):
        return {
            'id' : self.identifier,
            'name': self.name,
            'altitude' : self.altitude,
            'latitude' : self.latitude,
            'longitude' : self.longitude,
            'date_start' : self.date_start,
        'date_end' : self.date_end,
        'region' : self.region,
        'measurements' : map(lambda x: x.to_dict(), self.measurements)
    }

    def __repr__(self):
        return "Station(name=%s)" % self.name

    def _get_id_as_str(self):
        return '%05d' % self.identifier

    def _get_file_name(self, version):
        values = {
            'recent' : ('tageswerte', 'KL', self._get_id_as_str(), 'akt.zip'),
            'historical' : ('tageswerte', self._get_id_as_str(), self.date_start, self.date_end, 'hist.zip'),
        }
        return '_'.join(values[version])


class Measurement:
    def __init__(self, date_raw, temperature, cloudy, rainfall, sunshine_duration, snowfall_height):
        self.date = date_as_datetime(date_raw)
        self.temperature = temperature
        self.cloudy = cloudy
        self.rainfall = rainfall
        self.sunshine_duration = sunshine_duration
        self.snowfall_height = snowfall_height

    def to_dict(self):
        return {
            'date' : self.date.strftime('%Y-%m-%d'),
            'temperature' : self.temperature,
            'cloudy': self.cloudy,
            'rainfall': self.rainfall,
            'sunshine_duration' : self.sunshine_duration,
            'snowfall_height' : self.snowfall_height
        }

    def __repr__(self):
        return "Measurement(date=%s)" % self.date

