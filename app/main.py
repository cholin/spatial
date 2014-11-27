# -*- coding: utf-8 -*-

import json
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from .models import Station, Measurement
from .exts import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/<date>')
def api(date):
    date_cmp = datetime.strptime(date, "%Y-%m-%d")
    qry = db.session.query(Measurement).filter(Measurement.date == date_cmp)
    measurements = [m.to_geojson() for m in qry.all()]
    return jsonify(measurements=measurements)

