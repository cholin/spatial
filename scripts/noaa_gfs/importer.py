import urllib2
import time
import os
from subprocess import check_output
from tempfile import NamedTemporaryFile
from datetime import datetime, date, timedelta
from urllib import urlencode
from app.exts import db

DEFAULT_URI='http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_hd.pl'
DEFAULT_INTERVALS = [12, 24, 36, 48, 96]

def forecast_download(date_from, date_to, intervals):
    """
        Downloads grib files from noaa for a time interval.
        This method returns a generator. To access the data you should loop
        through (return value is a (date, interval, data) tuple)
    """

    # get forecasts for temperature and rainfall for bounding box of germany
    params = urlencode({
        'lev_2_m_above_ground' : 'on',
        'var_PWAT' : 'on',
        'var_TMP' : 'on',
        'subregion' : '',
        'leftlon' : '5',
        'rightlon' : '16',
        'toplat' : '56',
        'bottomlat' : '46'
    })

    delta = date_to - date_from
    for i in range(delta.days + 1):
        for hour in [0, 6, 12, 18, 24]:
            current = date_from + timedelta(days = i, hours = hour)
            for interval in intervals:
                f_subset = 'dir=%2Fgfs.{date}{hour:02}%2Fmaster&'\
                           'file=gfs.t{hour:02}z.mastergrb2f{interval:02}'
                subset = f_subset.format(date=current.strftime("%Y%m%d"),
                                         hour=hour,
                                         interval=interval)

                url = DEFAULT_URI
                args = '{}&{}'.format(params, subset)
                try:
                    response = urllib2.urlopen('{}?{}'.format(url, args))
                    data = response.read()
                except urllib2.HTTPError:
                    data = None

                yield current, interval, data


def forecast_noaa_import(date_from, date_to, table, intervals=DEFAULT_INTERVALS):
    """
        Imports noaa gfs forecast data for a given time interval. With table you
        specify into which sql table the rasters should be saved. This function
        returns a generator in the form (date, interval, sql). To actually
        import the data, you have to execute sql (return value) manually.
    """
    date_from = datetime.strptime(date_from, "%Y-%m-%d")

    # if no date is given, use today
    if date_to is None:
        date_to = datetime.combine(date.today(), datetime.min.time())

    # loop over downloaded grib files
    for current, interval, data in forecast_download(date_from, date_to, intervals):
        sql = None
        if data is not None:
            # save data in tmp file
            with NamedTemporaryFile() as f:
                f.write(data)
                f.flush()

                # run raster2psql and save output
                cmd = ['raster2pgsql',
                       '-s', '4326', # assign output raster with SRID
                       '-a',         # append data to sql table
                       f.name,
                       table,
                ]

                # discard 'Processing ...' output on stderr
                with open(os.devnull, 'wb') as DEVNULL:
                    sql = check_output(cmd, stderr=DEVNULL)

        yield current, interval, sql

        # sleep for 0.5 seconds to prevent ip blocking
        time.sleep(0.5)

