# open-topo-map

Scripts zur Darstellung der topografischen Flächen in Schleswig-Holstein



## Setup Application

```
sudo apt install python3 python3-venv
git clone https://github.com/oklabflensburg/open-topo-map.git
cd open-topo-map/tools
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
deactivate
```


## Run script

```
cd tools
python3 tile_downloader.py 843 18685
```


## Render bbox

```
psql -U postgres -h localhost -d postgres -p 5433 -c "WITH j (ars, gen, wkb_geometry) AS (SELECT ars, gen, ST_Union(wkb_geometry) FROM vg250gem GROUP BY gen, ars) SELECT ars, gen, ST_Extent(wkb_geometry) FROM j GROUP BY gen, ars;" -o vg250gem_bbox.csv

psql -U postgres -h localhost -d postgres -p 5433 -c "WITH j (ars, gen, wkb_geometry) AS (SELECT ars, gen, ST_Union(wkb_geometry) FROM vg250vwg GROUP BY gen, ars) SELECT ars, gen, ST_Extent(wkb_geometry) FROM j GROUP BY gen, ars;" -o vg250vwg_bbox.csv

psql -U postgres -h localhost -d postgres -p 5433 -c "WITH j (ars, gen, wkb_geometry) AS (SELECT ars, gen, ST_Union(wkb_geometry) FROM vg250krs GROUP BY gen, ars) SELECT ars, gen, ST_Extent(wkb_geometry) FROM j GROUP BY gen, ars;" -o vg250krs_bbox.csv

psql -U postgres -h localhost -d postgres -p 5433 -c "WITH j (ars, gen, wkb_geometry) AS (SELECT ars, gen, ST_Union(wkb_geometry) FROM vg250rbz GROUP BY gen, ars) SELECT ars, gen, ST_Extent(wkb_geometry) FROM j GROUP BY gen, ars;" -o vg250rbz_bbox.csv

psql -U postgres -h localhost -d postgres -p 5433 -c "WITH j (ars, gen, wkb_geometry) AS (SELECT ars, gen, ST_Union(wkb_geometry) FROM vg250lan GROUP BY gen, ars) SELECT ars, gen, ST_Extent(wkb_geometry) FROM j GROUP BY gen, ars;" -o vg250lan_bbox.csv

psql -U postgres -h localhost -d postgres -p 5433 -c "WITH j (ars, gen, wkb_geometry) AS (SELECT ars, gen, ST_Union(wkb_geometry) FROM vg250sta GROUP BY gen, ars) SELECT ars, gen, ST_Extent(wkb_geometry) FROM j GROUP BY gen, ars;" -o vg250sta_bbox.csv
```


## SH DGM1 tile raster inserts

```
psql -U oklab -h localhost -d oklab -p 5432 < ../data/sh_dgm1_meta_schema.sql
```

```
cd tools
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 insert_epsg_csv.py --env ../.env --src ../data/sh_dgm1_tiles.csv --verbose
deactivate
```
