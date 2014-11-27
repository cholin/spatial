# -*- coding: utf-8 -*-

from flask import Flask, render_template
from .exts import db
from .main import main


def create_app(config=None):
    """Creates the Flask app."""
    app = Flask(__name__)

    # load config - http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('../config.cfg', silent=True)

    # init flask-sqlalchemy
    db.init_app(app)

    for blueprint in [main]:
        app.register_blueprint(blueprint)

    return app
