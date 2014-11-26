# -*- coding: utf-8 -*-

import zipfile
import csv
import ftplib
import json
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon
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

        # parse stations, download each zip, unpack it and parse data
        print("Parsing data...")
        for i, station in enumerate(self._parse_stations(data, limit)):
            print("\t%d. %s " % (i+1, station.name))
            self.stations.append(station)
        print("Parsing done.")

        # generate voronoi diagram to generate region polygon for each station
        self._generate_voronoi()

        # yield parsed stations
        for station in self.stations:
            yield station

        print("\n==> imported %d stations" % len(self.stations))


    def _get_stations_raw(self, path):
        """ get stations file from ftp """
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
                if limit is not None and i >= int(limit):
                    raise StopIteration
            except IndexError:
                pass

    def _parse_station(self, raw):
        coords = Point(float(raw[5]), float(raw[4]))
        station = Station(raw[0], raw[6], coords, raw[3], raw[1], raw[2])
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


        # return all measurement values
        reader = list(csv.reader(data, delimiter=';', skipinitialspace=True))[1:-1]
        return [Measurement(row[1], row[3], row[5], row[13], row[14], row[15]) for row in reader]


    def _generate_voronoi(self):
        # get all lat/long tuples for every station
        points = np.zeros((len(self.stations), 2))
        for i,s in enumerate(self.stations):
            points[i,:] = list(s.coords.coords)[0]

        # generate voronoi and get polygons for each region
        vor = Voronoi(points)
        polygons = []
        for region in vor.regions:
            polygons.append(vor.vertices[region] if -1 not in region else [])

        # load germany border polygon (for intersection test)
        with open("scripts/importer/germany_border.geojson", "r") as f:
            raw = json.load(f)
            coordinates_ger = raw['features'][0]['geometry']['coordinates']
            polygons_ger = [[p[0], []] for p in coordinates_ger]
            germany = MultiPolygon(polygons_ger)

        # save each voronoi region polygon
        for i, p in enumerate(vor.point_region):
            if len(polygons[p]) > 0:
                # add first point as last point (needed for postgis)
                polygon = Polygon(np.append(polygons[p],[polygons[p][0]],axis=0))

                # limit polygons to border of germany
                polygon_shaped = polygon.intersection(germany)

                # save it
                self.stations[i].region = polygon_shaped
