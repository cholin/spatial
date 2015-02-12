# -*- coding: utf-8 -*-

import os
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


class Importer:

    def __init__(self, host, path):
        self.host = host
        self.path = path
        self.ftp = ftp_connect(self.host)


    def do_import(self):
        """
            Imports data from the ftp server of DWD (german weather service).
            It returns a generator with (station, measurements)
        """
        # station file is iso8859 encoded
        data = self._get_stations_raw(self.path).decode("iso-8859-1").encode("utf-8")

        # parse stations, download each zip, unpack it and parse data and yield
        # it
        for station in self._parse_stations(data):
            measurements = self._parse_measurements(station)
            if len(measurements) > 0:
                yield station, measurements


    def _get_stations_raw(self, path):
        """ get stations file from ftp """
        files = list(ftp_list(self.ftp, path))
        stations_file = [f.strip() for f in files if f.endswith('.txt')][0]
        return ftp_get_file(self.ftp, stations_file).getvalue()


    def _parse_stations(self, data):
        """ parses raw csv stations file """
        # first two lines do not contain data
        lines = data.split('\r\n')[2:-1]
        reader = csv.reader(lines, delimiter=' ', skipinitialspace=True)
        for row in reader:
            try:
                station = self._parse_station(row)
                yield self._parse_station(row)
            except IndexError:
                pass

    def _parse_station(self, raw):
        """ parses a line of raw csv station file """
        coords = Point(float(raw[5]), float(raw[4]))
        return Station(raw[0], raw[6], coords, raw[3], raw[1], raw[2])


    def _parse_measurements(self, station):
        """ 
            downloads corresponding zip for a station to extract measurements
            and returns them.
        """
        try:
            fp = ftp_get_file(self.ftp, station._get_file_name('hourly'))
        except:
            return []

        data = StringIO()
        with zipfile.ZipFile(fp) as archive:
            # get file name for data
            name = ([x for x in archive.namelist() if x.startswith('produkt')])[0]
            # extract file into data
            data = archive.open(name)

        # return all measurement values
        reader = list(csv.reader(data, delimiter=';', skipinitialspace=True))[1:-1]
        return [Measurement(row[1], row[4], None, None, None, None) for row in reader]


    @classmethod
    def generate_regions(cls, points):
        """
           Calculate regions for given points with voronoi. This is useful if
           you want to see which station is the nearest for a given point.
        """

        # add big bounding box for germany. with this the resulting cells won't
        # be affected by infinity points and therefor union of all cells is
        # equal of intersection country polygon
        box = [[-20,60], [30, 60], [30, 40], [-20, 40]]
        points.extend(box)

        # create matrix for every point
        matrix = np.zeros((len(points), 2))
        for i,p in enumerate(points):
            matrix[i,:] = p

        # generate voronoi and get polygons for each region
        vor = Voronoi(matrix)
        polygons = [vor.vertices[r] for r in vor.regions]

        # load germany border polygon (for intersection test) otherwise the
        # regions can be outside of germany
        script_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_path, 'germany_border.geojson')
        with open(path, "r") as f:
            raw = json.load(f)
            coordinates_ger = raw['features'][0]['geometry']['coordinates']
            polygons_ger = [[p[0], []] for p in coordinates_ger]
            germany = MultiPolygon(polygons_ger)

        # save each voronoi region polygon (discard our bounding box)
        for point_idx,region_idx in enumerate(vor.point_region[:-len(box)]):
            polygon = None
            if len(polygons) > region_idx:
                p_tmp = polygons[region_idx]
                if len(p_tmp) > 0:
                    # add first point as last point (needed for postgis)
                    p = Polygon(np.append(p_tmp,[p_tmp[0]],axis=0))

                    # limit polygons to border of germany
                    polygon = p.intersection(germany)

            yield (point_idx, polygon)
