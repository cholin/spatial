# -*- coding: utf-8 -*-

import json
import argparse
from .importer import Importer

DEFAULT_HOST = 'ftp.dwd.de'
DEFAULT_DIR = 'pub/CDC/observations_germany/climate/daily/kl/recent/'
DEFAULT_FILE_NAME = 'weather.json'

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--limit", help="limit", default=None)
parser.add_argument("--file", help="export file name", default=DEFAULT_FILE_NAME)
parser.add_argument("--host", help="ftp host url", default=DEFAULT_HOST)
parser.add_argument("--dir", help="ftp path", default=DEFAULT_DIR)
args = parser.parse_args()

importer = Importer(args.host, args.dir)
for station in importer.do_import(args.limit):
     print("Added %s (%d measurements)" % (station.name, len(station.measurements)))

with open(args.file, 'w') as f:
     data = map(lambda x: x.to_dict(), importer.stations)
     json.dump(data, f, sort_keys = True, indent = 4, ensure_ascii=False)
