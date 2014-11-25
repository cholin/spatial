# -*- coding: utf-8 -*-

import json
import argparse
from .importer import Importer

DEFAULT_HOST = 'ftp.dwd.de'
DEFAULT_DIR = 'pub/CDC/observations_germany/climate/daily/kl/recent/'
DEFAULT_FILE_NAME = 'weather.json'

parser = argparse.ArgumentParser()
parser.parse_args()
parser.add_argument("host", help="ftp host url", nargs='?', default=DEFAULT_HOST)
parser.add_argument("dir", help="directory", nargs='?', default=DEFAULT_DIR)
parser.add_argument("file", help="file name", nargs='?', default=DEFAULT_FILE_NAME)
args = parser.parse_args()

importer = Importer(args.host, args.dir)
for station in importer.do_import():
     print("%s: %d" % (station.name, len(station.measurements)))

with open(args.file, 'w') as f:
     data = map(lambda x: x.to_dict(), importer.stations)
     json.dump(data, f, sort_keys = True, indent = 4, ensure_ascii=False)
