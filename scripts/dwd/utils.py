# -*- coding: utf-8 -*-

import numpy as np
from datetime import datetime

def date_as_datetime(raw):
    return datetime.strptime(raw, '%Y%m%d%H')
