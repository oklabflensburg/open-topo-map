-- HILFSTABELLE METADATEN BIOTOPENCODE SCHLESWIG-HOLSTEIN
DROP TABLE IF EXISTS sh_dgm1_meta CASCADE;

CREATE TABLE IF NOT EXISTS sh_dgm1_meta (
  id SERIAL,
  crs VARCHAR,
  range_min_x INT,
  range_min_y INT,
  range_max_x INT,
  range_max_y INT,
  width INT,
  height INT,
  undefined_values INT,
  file_name VARCHAR,
  flags BIT(32),
  wkb_geometry GEOMETRY(GEOMETRY, 4326),
  PRIMARY KEY(id)
);


-- GEOMETRY INDEX
CREATE INDEX IF NOT EXISTS sh_dgm1_meta_wkb_geometry_idx ON sh_dgm1_meta USING GIST (wkb_geometry);
