# -*- coding: utf-8 -*-

import json
from flask import Blueprint, render_template
from .models import Station
from .exts import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    points = []
    regions = []
    for station in db.session.query(Station).all():
        points.append(station.geom_as_geojson)
        regions.append(station.region_as_geojson)

    return render_template('index.html', geojson=json.dumps(points + regions))
