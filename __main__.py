# -*- coding: utf-8 -*-

import json
from importer import Importer

HOST = 'ftp.dwd.de'
DIR_BASE = 'pub/CDC/observations_germany/climate/'
DAILY_HISTORIC = DIR_BASE + 'daily/kl/historical/'
DAILY_RECENT   = DIR_BASE + 'daily/kl/recent/'


importer = Importer(HOST, DAILY_RECENT)
data = {}
for station in importer.do_import():
    print("%s: %d" % (station.name, len(station.sensors)))
    data[station.name] = station.to_dict()

with open('export.json', 'w') as f:
     json.dump(data, f, sort_keys = True, indent = 4, ensure_ascii=False)
