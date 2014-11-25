# -*- coding: utf-8 -*-

import zipfile
import csv
import ftplib
import numpy as np
from scipy.spatial import Voronoi
from datetime import datetime
from StringIO import StringIO
from models import Station, Measurement
from ftp import ftp_connect, ftp_list, ftp_get_file
from utils import date_as_datetime


class Importer:

    def __init__(self, host, path):
        self.host = host
        self.path = path
        self.ftp = ftp_connect(self.host)
        self.stations = []


    def do_import(self, limit = None):
        print("Importing from %s (%s)\n" % (self.host, self.path))
        # station file is iso8859 encoded
        data = self._get_stations_raw(self.path).decode("iso-8859-1").encode("utf-8")
        for station in self._parse_stations(data, limit):
            self.stations.append(station)
            yield station
        self._generate_voronoi()
        print("\n==> imported %d stations" % len(self.stations))


    def _get_stations_raw(self, path):
        # load stations file
        files = list(ftp_list(self.ftp, path))
        stations_file = [f.strip() for f in files if f.endswith('.txt')][0]
        return ftp_get_file(self.ftp, stations_file).getvalue()

    def _parse_stations(self, data, limit = None):
        # first two lines do not contain data
        lines = data.split('\r\n')[2:-1]
        reader = csv.reader(lines, delimiter=' ', skipinitialspace=True)
        i = 0
        for row in reader:
            try:
                station = self._parse_station(row)
                if len(station.measurements) > 0:
                    yield self._parse_station(row)
                    i += 1
                if limit is not None and i >= limit:
                    raise StopIteration
            except IndexError:
                pass

    def _parse_station(self, raw):
        station = Station(raw[0], raw[6], raw[3], raw[4], raw[5], raw[1], raw[2])
        station.measurements = self._parse_measurements(station)
        return station


    def _parse_measurements(self, station):
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


        # return all measurement values - for the moment only wind and temperature
        reader = list(csv.reader(data, delimiter=';', skipinitialspace=True))[1:-1]
        return [Measurement(row[1], row[3], row[5], row[13], row[14], row[15]) for row in reader]


    def _generate_voronoi(self):
        # get all lat/long tuples for every station
        points = np.zeros((len(self.stations), 2))
        for i,s in enumerate(self.stations):
             points[i,:] = s.lonlat

        # generate voronoi and get polygons for each region
        vor = Voronoi(points)
        polygons = []
        for region in vor.regions:
            polygons.append(vor.vertices[region] if -1 not in region else [])

        # save each voronoi region polygon
        for i, p in enumerate(vor.point_region):
            polygon = list(map(list, polygons[p]))
            if len(polygon) > 0:
                # add first point as last point (needed for postgis)
                self.stations[i].region = polygon + [polygon[0]]
