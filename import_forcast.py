import datetime
import urllib2


def download_forecasts():
    """Downloads forecasts from NOAA GFS 0.5 Grid for Germany.

    Downloaded subregion 5.9166670 (west), 14.975 (east), 
    55.052222 (north), 47.270108 (south) corresponds to
    the reactangle boundry of Germany.
    """
    timestr = datetime.datetime.now().strftime("%Y%m%d")# get forcasts calculated today
    timestr +='00' # get the forecast calculation from midnight
    for forecast in ["12", "24", "36", "48", "72", "96", "120", "144"]:
	for t in ["TMIN","TMAX"]: # get max and min temperature only
	    url = 'http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_hd.pl?file=gfs.t00z.mastergrb2f{}&var_{}=ON&subregion=&leftlon=5.916667&rightlon=14.975&toplat=55.052222&bottomlat=47.270108&dir=%2Fgfs.{}%2Fmaster'.format(forecast, t, timestr)
	    print url
            response = urllib2.urlopen(url)
            data = response.read()
            with open("/tmp/germany_raster_{}_f{}_{}.grib2".format(timestr, forecast, t), "wb") as fgrib:
                fgrib.write(data)

if __name__ == '__main__':
    download_forecasts()
