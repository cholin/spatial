# -*- coding: utf-8 -*-

import json
import io
from flask import Blueprint, render_template, request, jsonify, send_file
from .models import Station, Measurement, Forecast


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/api/measurements/<mtype>')
@main.route('/api/measurements/<mtype>/<date>')
def api_measurements(mtype, date = None):
    date, data = Measurement.all(mtype, date)
    measurements = [m.to_geojson() for m in data]
    return jsonify(date = date,  measurements=measurements)


@main.route('/api/forecasts/<ftype>')
@main.route('/api/forecasts/<ftype>/<date>')
def api_forecasts(ftype, date = None):
    raster_img = Forecast.get_raster_img(ftype, date)
    return send_file(io.BytesIO(raster_img), mimetype='image/png')
