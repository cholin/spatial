# -*- coding: utf-8 -*-

import json
import io
from flask import Blueprint, render_template, request, jsonify, send_file
from .models import Station, Measurement, Forecast


main = Blueprint('main', __name__)


@main.route('/')
def index():
    """
        Delivers static template for our web app. All data will be fetched
        through api_*() functions via leaflet.
    """
    return render_template('index.html')


@main.route('/api/measurements/<mtype>')
@main.route('/api/measurements/<mtype>/<date>')
def api_measurements(mtype, date = None):
    """
        Returns a data for a given measurement type encoded in vector space as
        geojson. If no date is given, today will be used.
    """
    date, data = Measurement.all(mtype, date)
    measurements = [m.to_geojson() for m in data]
    return jsonify(date = date,  measurements=measurements)


@main.route('/api/forecasts/<ftype>')
@main.route('/api/forecasts/<ftype>/<date>')
def api_forecasts(ftype, date = None):
    """
        Returns a raster encoded in a PNG image for given forecast type and an
        optional date. If no date is given, today will be used.
    """
    raster_img = Forecast.get_raster_img(ftype, date)
    return send_file(io.BytesIO(raster_img), mimetype='image/png')
