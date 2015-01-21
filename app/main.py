# -*- coding: utf-8 -*-

import json
import io
from datetime import datetime, date, time
from flask import Blueprint, render_template, request, jsonify, send_file
from .models import Station, Measurement, Forecast
from .utils import get_datetime


main = Blueprint('main', __name__)


@main.route('/')
def index():
    """
        Delivers static template for our web app. All data will be fetched
        through api_*() functions via leaflet.
    """
    return render_template('index.html')


@main.route('/api/measurements/<mtype>')
@main.route('/api/measurements/<mtype>/<mdate>')
@main.route('/api/measurements/<mtype>/<mdate>/<mhours>')
def api_measurements(mtype, mdate = None, mhours = None):
    """
        Returns a data for a given measurement type encoded in vector space as
        geojson. If no date is given, today will be used.
    """
    mdatetime = get_datetime(mdate, mhours)
    data = Measurement.all(mtype, mdatetime)
    measurements = [m.to_geojson() for m in data]
    return jsonify(measurements=measurements)


@main.route('/api/forecasts/<ftype>')
@main.route('/api/forecasts/<ftype>/<fdate>')
@main.route('/api/forecasts/<ftype>/<fdate>/<fhours>')
def api_forecasts(ftype, fdate = None, fhours = None):
    fdatetime = get_datetime(fdate, fhours)
    print(fdatetime)
    forecasts = Forecast.get_forecasts_for_date(ftype, fdatetime)
    return jsonify(forecasts = [f.to_dict() for f in forecasts])


@main.route('/api/forecasts/raster/<ftype>/<rid>')
def api_forecasts_raster(ftype, rid = None):
    """
        Returns a raster encoded in a PNG image for given forecast type and an
        optional date. If no date is given, today will be used.
    """
    raster_img = Forecast.get_raster_img_for_rid(ftype, rid)
    return send_file(io.BytesIO(raster_img), mimetype='image/png')
