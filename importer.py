# -*- coding: utf-8 -*-

import zipfile
import csv
import ftplib
from datetime import datetime
from StringIO import StringIO
from models import Station, SensorValue
from ftp import ftp_connect, ftp_list, ftp_get_file
from utils import date_as_datetime


class Importer:

    def __init__(self, host, path):
        self.host = host
        self.path = path
        self.ftp = ftp_connect(self.host)


    def do_import(self):
        data = self._get_stations_raw(self.path)
        return self._parse_stations(data)

    def _get_stations_raw(self, path):
        # load stations file
        files = list(ftp_list(self.ftp, path))
        stations_file = [f.strip() for f in files if f.endswith('.txt')][0]
        return ftp_get_file(self.ftp, stations_file).getvalue()

    def _parse_stations(self, data):
        # first two lines do not contain data
        lines = data.split('\r\n')[2:-1]
        reader = csv.reader(lines, delimiter=' ', skipinitialspace=True)
        for row in reader:
            try:
                station = self._parse_station(row)
                if len(station.sensors) > 0:
                    yield self._parse_station(row)
            except IndexError:
                pass

    def _parse_station(self, raw):
        station = Station(raw[0], raw[6], raw[3], raw[4], raw[5], raw[1], raw[2])
        station.sensors = self._parse_sensors(station)
        return station


    def _parse_sensors(self, station):
        try:
            fp = ftp_get_file(self.ftp, station._get_file_name('recent'))
        except:
            return []

        data = StringIO()
        with zipfile.ZipFile(fp) as archive:
            # get file name for data
            name = ([x for x in archive.namelist() if x.startswith('produkt_klima_Tageswerte')])[0]
            # extract file into data
            data = archive.open(name)


        # return all sensor values - for the moment only wind and temperature
        sensor_values = []
        reader = list(csv.reader(data, delimiter=';', skipinitialspace=True))[1:-1]
        return [SensorValue(row[1], row[3], row[8]) for row in reader]



