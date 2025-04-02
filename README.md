# open-topo-map

Scripts zur Darstellung der topografischen Flächen in Schleswig-Holstein


## Download SH DGM1 XYZ

```sh
cd tools
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 dgm1_hvd_downloader.py --src ../data/DGM1_SH__Massendownload.geojson --dst /data/raw/sh/dgm1 --verbose
deactivate
```


## SH DGM1 tile raster inserts

```sh
psql -U oklab -h localhost -d oklab -p 5432 < ../data/sh_dgm1_meta_schema.sql
```

```sh
cd tools
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 insert_epsg_csv.py --env ../.env --src ../data/sh_dgm1_tiles.csv --verbose
deactivate
```


---


## How to Contribute

Contributions are welcome! Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) guide for details on how to get involved.


---


## License

This repository is licensed under [CC0-1.0](LICENSE).
