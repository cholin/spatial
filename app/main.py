# -*- coding: utf-8 -*-

import json
from flask import Blueprint, render_template
from .models import Station
from .exts import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    regions = [s.region_as_geojson for s in db.session.query(Station).all()]
    return render_template('index.html', geojson=json.dumps(regions))
