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
        self.sensors = []
        self.polygon = []

    @property
    def latlon(self):
        return (self.latitude, self.longitude)

    def to_dict(self):
        return {
            'id' : self.identifier,
            'name': self.name,
            'altitude' : self.altitude,
            'latitude' : self.latitude,
            'longitude' : self.longitude,
            'date_start' : self.date_start,
            'date_end' : self.date_end,
            'sensors' : map(lambda x: x.to_dict(), self.sensors)
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


class SensorValue:
    def __init__(self, date_raw, temperature, wind):
        self.date = date_as_datetime(date_raw)
        self.temperature = temperature
        self.wind = wind

    def to_dict(self):
        return {
            'date' : self.date.strftime('%Y-%m-%d'),
            'temperature' : self.temperature,
            'wind' : self.wind
        }

    def __repr__(self):
        return "SensorValue(date=%s)" % self.date

