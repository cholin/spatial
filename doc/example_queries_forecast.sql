-- MIN temp 7 days forecast for berlin
SELECT 12 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As min_temperature from raster_20150108_12_tmin UNION
SELECT 24 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As min_temperature from raster_20150108_24_tmin UNION
SELECT 36 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As min_temperature from raster_20150108_36_tmin UNION
SELECT 48 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As min_temperature from raster_20150108_48_tmin UNION
SELECT 72 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As min_temperature from raster_20150108_72_tmin UNION
SELECT 96 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As min_temperature from raster_20150108_96_tmin UNION
SELECT 120 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As min_temperature from raster_20150108_120_tmin UNION
SELECT 144 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As min_temperature from raster_20150108_144_tmin order by time ASC;


-- MAX temp 7 days forecast for berlin
SELECT 12 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As max_temperature from raster_20150108_12_tmax UNION
SELECT 24 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As max_temperature from raster_20150108_24_tmax UNION
SELECT 36 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As max_temperature from raster_20150108_36_tmax UNION
SELECT 48 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As max_temperature from raster_20150108_48_tmax UNION
SELECT 72 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As max_temperature from raster_20150108_72_tmax UNION
SELECT 96 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As max_temperature from raster_20150108_96_tmax UNION
SELECT 120 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As max_temperature from raster_20150108_120_tmax UNION
SELECT 144 AS time, ST_Value (rast, ST_PointFromText('POINT(13.38 52.51)', 4326)) As max_temperature from raster_20150108_144_tmax order by time ASC;
