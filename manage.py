# -*- coding: utf-8 -*-

from flask.ext.script import Manager
from app import create_app

# create app
app = create_app()
manager = Manager(app)

# import scripts
from scripts import * 

if __name__ == '__main__':
    manager.run()
