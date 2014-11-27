# -*- coding: utf-8 -*-

import json
from datetime import datetime
from flask import Blueprint, render_template, request
from .models import Station, Measurement
from .exts import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    param = request.args.get('date', "2014-07-01")
    date = datetime.strptime(param, "%Y-%m-%d")
    qry = db.session.query(Measurement).filter(Measurement.date == date)
    measurements = [m.to_geojson() for m in qry.all()]
    return render_template('index.html', geojson=json.dumps(measurements))
