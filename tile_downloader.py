#!./venv/bin/python

import os
import sys
import time
import httpx
import shutil
import magic

from pyproj import Proj, transform
from fake_useragent import UserAgent
from pathlib import Path

def transform_projection(lat, lng):
    inProj = Proj('EPSG:25832')
    outProj = Proj('EPSG:4326')

    y1, x1 = (lat, lng)

    coords = transform(inProj, outProj, y1, x1)

    return coords


def unpack_download(archive_path, target_path):
    shutil.unpack_archive(archive_path, target_path)


def load_data(target_path):
    with open(target_path, 'r') as f:
        content = f.read()

        return content

    return None


def save_download(download_path, data):
    Path('./tmp').mkdir(parents=True, exist_ok=True) 

    with open(download_path, 'wb') as f:
        f.write(data)


def get_mime_type(download_path):
    mime_type = magic.from_file(download_path, mime=True)

    return mime_type


def rename_download(download_path, archive_path):
    os.rename(download_path, archive_path)


def data_download(url):
    r = httpx.get(url)

    if r.status_code == httpx.codes.OK:
        return r.content

    return None


def job_request(id_code, user_agent):
    time_stamp = int(time.time())
    headers = {'Content-Type': 'application/json', 'User-Agent': user_agent}
    url = f'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/multi.php?action=status&job={id_code}&_={time_stamp}'

    r = httpx.get(url, headers=headers)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def dgm_request(tile_name, tile_id, user_agent):
    time_stamp = int(time.time())
    headers = {'Content-Type': 'application/json', 'User-Agent': user_agent}
    url = f'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/multi.php?url={tile_name}.xyz&buttonClass=file1&id={tile_id}&type=dgm1&action=start&_={time_stamp}'

    r = httpx.get(url, headers=headers)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def tile_request(tile_id, user_agent):
    headers = {'Content-Type': 'application/json', 'User-Agent': user_agent}
    url = f'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/_ajax/details.php?type=dgm1&id={tile_id}'

    r = httpx.get(url, headers=headers)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def fetch_data(tile_id):
    ua = UserAgent()

    dgm_code = tile_request(tile_id, ua.random)
    print(dgm_code)
    tile_name = dgm_code['object']['kachelname']
    
    id_code = dgm_request(tile_name, tile_id, ua.random)
    print(id_code)
    job_id = id_code['id']
    
    user_agent = ua.random

    job_status = job_request(job_id, user_agent)
    print(job_status)

    while job_status['status'] != 'done':
        time.sleep(1)
        job_status = job_request(job_id, user_agent)
        print(job_status)

    data = data_download(job_status['downloadUrl'])
    download_path = Path(f'./tmp/{job_id}')

    save_download(download_path, data)
    mime_type = get_mime_type(download_path)
    file_format = mime_type.split('/')

    if len(file_format) == 0:
        print('Error: no file extension detected')
        sys.exit(1)
    
    file_extension = file_format[-1]
    archive_path = Path(f'./tmp/{job_id}.{file_extension}')
    target_path = Path(f'./tmp/{job_id}')
    content_path = Path(f'./tmp/{job_id}/{tile_name}.xyz')
    
    rename_download(download_path, archive_path)
    unpack_download(archive_path, target_path)

    content = load_data(content_path)
    print(content)


def main():
    for tile_id in range(1, 18685):
        print(tile_id)
        fetch_data(tile_id)

if __name__ == '__main__':
    main()
