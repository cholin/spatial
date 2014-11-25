

  CREATE TABLE stations
  (
  id int not null primary key,
  name varchar(255),
  altitude = int,
  );
  SELECT AddGeometryColumn('stations', 'geo', 4326, 'POINT', 2 );
  SELECT AddGeometryColumn('stations', 'coverage', 4326, 'POLYGON', 2 );
  -- coverage is voronoi cell
  
  
  
  CREATE TABLE sensors
  (
  id int not null primary key,
  type varchar(255),
  value float,
  date datetime
  );
  SELECT AddGeometryColumn('sensors', 'geo', 4326, 'POINT', 2 );
  -- 4326 is WGS84 projection
