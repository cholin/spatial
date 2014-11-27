# -*- coding: utf-8 -*-

from flask import Flask, render_template
from .exts import db
from .main import main


def create_app(config=None):
    """Creates the Flask app."""
    app = Flask(__name__)

    configure_app(app)
    configure_extensions(app)

    for blueprint in [main]:
        app.register_blueprint(blueprint)

    return app


def configure_app(app):
    # http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('../default.cfg')
    app.config.from_pyfile('../config.cfg', silent=True)


def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)
