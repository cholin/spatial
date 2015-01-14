#!/bin/bash

PSQL_CMD="psql -U <USERNAME> -d <DATABASE>"
DATE="2015011300"
TABLE="forecast"

for i in 12 24 36 48 72 96 120 144 ; do
  grib_file="/tmp/germany_raster_${DATE}_f${i}_TMIN.grib2"
  forecast_type="temperature"
  date_calc="2015-01-12 00:00:00"
  date_forecast="$i hours"
  range="min"
  # -s Assign output raster with specified SRID.
  # -I Create a GiST index on the raster column.
  # -b Index (1-based) of band to extract from raster.
  # -C Apply raster constraints-
  # -a Append raster(s) to an existing table.
  # -M Vacuum analyze the raster table.
  raster2pgsql -s 4326 -I -a -b 1 -C -M "$grib_file" $TABLE  | $PSQL_CMD
  rid_qry="SELECT rid FROM forecasts ORDER BY rid DESC LIMIT 1"
  qry="UPDATE forecast
       SET
         type='$forecast_type',
         subtype='$range',
         date ='$date_calc',
         interval='$date_forecast'
       WHERE rid=($rid_qry)";
  echo $qry | $PSQL_CMD;
  echo "Added $grib_file"
done;

#for i in 12 24 36 48 72 96 120 144; do
#  grib_file="/tmp/germany_raster_${DATE}_f${i}_TMAX.grib2"
#  raster="raster_20150108_${i}_TMAX"
#  raster2pgsql -s 4326 -I -b 1 -C -M $grib_file $raster | $PSQL_CMD;
#done;
