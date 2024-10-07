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


## Download ALKIS®

Tool to automate the download from the opendata [ALKIS®](https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/dl-alkis.html) files for Schleswig-Holstein

```
cd tools
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 alkis_downloader.py 1 18000 --path /data --verbose
deactivate
```


## Import ALKIS®

Make sure to adapt database connection string to your needs

```
cd /data/sh/alkis
for i in *.zip; do f=$(basename $i | sed -e 's/.zip$//'); n=$(echo $f | sed -e 's/.*_//'); echo $n; unzip -o $f && [[ -e ${n}.xml ]] || gunzip "${n}.xml.gz" && ogr2ogr -f "PostgreSQL" PG:"dbname=oklab user=oklab port=5432 host=localhost" -nlt CONVERT_TO_LINEAR  -lco GEOMETRY_NAME=geom -lco SPATIAL_INDEX=GIST -update -overwrite -skipfailures -s_srs EPSG:25832 -t_srs EPSG:4326 -progress --config PG_USE_COPY YES $n.xml ax_flurstueck ax_gebaeude && rm -v ${n}.gfs ${n}.xml; done
```
