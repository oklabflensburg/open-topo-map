# open-topo-map

Scripts zur Darstellung der topografischen Flächen in Schleswig-Holstein


## Setup Application

```
sudo apt install python3 virtualenv tree git jq
git clone https://github.com/oklabflensburg/open-topo-map.git
cd open-topo-map
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Run script

```
python tile_downloader.py 843 18685
```
