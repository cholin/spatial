#!/bin/bash

# TODO: this needs to be done by the python importer
for i in 12 24 36 48 72 96 120 144 ; do raster2pgsql -s 4326 -I -b 1 -C -M  /tmp/germany_raster_2015010800_f${i}_TMIN.grib2 raster_20150108_${i}_TMIN | psql -U gisuser -d spatial; done;
for i in 12 24 36 48 72 96 120 144; do raster2pgsql -s 4326 -I -b 1 -C -M  /tmp/germany_raster_2015010800_f${i}_TMAX.grib2 raster_20150108_${i}_TMAX | psql -U gisuser -d spatial; done;
