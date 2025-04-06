# open-topo-map

Scripts zur Darstellung der DGM1 Topografie Kacheln in Schleswig-Holstein.


## Download SH DGM1 XYZ

### Python
```sh
cd tools/python
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 dgm1_hvd_downloader.py --src ../data/DGM1_SH__Massendownload.geojson --dst /data/raw/sh/dgm1 --verbose
deactivate
```

### Go


1) Navigate to the directory containing the Go tools:
```sh
cd tools/go
```

2) Run the program with the **-help** flag to display usage information:

```sh
go run dgm1_hvd_downloader.go -help
```

3) Run with **Download Mode** enabled, using the specified source and destination file paths. This will download all files:
- Replace ```/your-src-path/your-file.geojson``` with the path to the GeoJSON file containing the downloadable features (e.g., ../data/DGM1_SH__Massendownload.geojson).
- Replace ```your-dst-path with the path``` to the directory where the downloaded files should be saved (e.g., /data/raw/sh/dgm1).

```sh
go run dgm1_hvd_downloader.go -v --download --src "/your-src-path/your-file.geojson" --dst "/your-dst-path"
```
Optionally, you can define start and end indices to specify a range of files to download:
```sh
go run dgm1_hvd_downloader.go -v --download --start 1000 --end 1999 --src "/your-src-path/your-file.geojson" --dst "/your-dst-path"
```

4) Run with **Verify Mode** enabled to check the downloaded files:
- Replace your-src-path with the path to the directory where the downloaded files are stored.
- Replace your-log-path/your-log-file.log with the path where you want the log file to be saved.
```sh
go run dgm1_hvd_downloader.go -v -verify --src "/your-src-path" --log "your-log-path/your-log-file.log"
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
