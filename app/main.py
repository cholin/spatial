# -*- coding: utf-8 -*-

import json
from flask import Blueprint, render_template, request, jsonify
from .models import Station, Measurement

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/<mtype>')
@main.route('/api/<mtype>/<date>')
def api(mtype, date = None):
    date, data = Measurement.all(mtype, date)
    measurements = [m.to_geojson() for m in data]
    return jsonify(date = date,  measurements=measurements)

