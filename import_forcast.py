import datetime
import urllib2


def download_forecasts():
    """Downloads forecasts from NOAA GFS 0.5 Grid for Germany.

    Downloaded subregion 5 (west), 15 (east),
    56 (north), 47 (south) corresponds to
    the reactangle boundry of Germany.
    """
    # get forcasts calculated today
    timestr = datetime.datetime.now().strftime("%Y%m%d")

    # get the forecast calculation from midnight
    timestr +='00'
    for forecast in ["12", "24", "36", "48", "72", "96", "120", "144"]:
        # get max and min temperature only
        for t in ["TMIN","TMAX"]:
            url = 'http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_hd.pl?file=gfs.t00z.mastergrb2f{}&lev_2_m_above_ground=on&var_{}=ON&subregion=&leftlon=5&rightlon=15&toplat=56&bottomlat=47&dir=%2Fgfs.{}%2Fmaster'.format(forecast, t, timestr)
            print(url)
            response = urllib2.urlopen(url)
            data = response.read()
            with open("/tmp/germany_raster_{}_f{}_{}.grib2".format(timestr, forecast, t), "wb") as fgrib:
                fgrib.write(data)

if __name__ == '__main__':
    download_forecasts()
