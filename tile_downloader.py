#!./venv/bin/python

import os
import sys
import time
import httpx
import pathlib
import shutil
import magic

from pyproj import Proj, transform
from fake_useragent import UserAgent


def transform_projection(lat, lng):
    inProj  = Proj('EPSG:25832')
    outProj = Proj('EPSG:4326')

    y1, x1 = (lat, lng)

    coords = transform(inProj, outProj, y1, x1)

    return coords


def unpack_download(id_code):
    shutil.unpack_archive(f'./tmp/{id_code}', f'./tmp/{id_code}.xyz')


def load_download(id_code):
    with open(f'./tmp/{id_code}', 'r') as f:
        content = f.read(data)

        return content

    return None


def save_download(id_code, data):
    pathlib.Path('./tmp').mkdir(parents=True, exist_ok=True) 

    with open(f'./tmp/{id_code}', 'wb') as f:
        f.write(data)


def mime_type(id_code):
    mime = magic.from_file(f'./tmp/{id_code}', mime=True)

    return mime


def rename_download(id_code, mime_type):
    print(mime_type)

    os.rename(f'./tmp/{id_code}', f'./tmp/{id_code}')


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


def dgm_request(dgm_code, user_agent):
    time_stamp = int(time.time())
    headers = {'Content-Type': 'application/json', 'User-Agent': user_agent}
    url = f'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/multi.php?url={dgm_code}.xyz&buttonClass=file1&id=6688&type=dgm1&action=start&_={time_stamp}'

    r = httpx.get(url, headers=headers)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def tile_request(user_agent):
    headers = {'Content-Type': 'application/json', 'User-Agent': user_agent}
    url = 'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/_ajax/details.php?title=325286075&kachelname=dgm1_32_528_6075_1_sh&filepath=32520_6070&hoehenbezu=DE_DHHN92_NH&quasigeoid=DE_AdV_GCG2005_QGH&e_datum=2007-03-25&a_datum=2007-03-25&e_datum_dmy=25.03.2007&a_datum_dmy=25.03.2007&jahr=2007&ogc_fid=6688&type=dgm1&id=6688&_uid=dgm16688'

    r = httpx.get(url, headers=headers)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def main():
    ua = UserAgent()

    dgm_code = tile_request(ua.random)
    print(dgm_code)
    
    id_code = dgm_request(dgm_code['object']['kachelname'], ua.random)
    print(id_code)
    
    user_agent = ua.random

    job_status = job_request(id_code['id'], user_agent)
    print(job_status)

    while job_status['status'] != 'done':
        time.sleep(1)
        job_status = job_request(id_code['id'], user_agent)
        print(job_status)


    data = data_download(job_status['downloadUrl'])
    save_download(id_code['id'], data)

    mime_type = mime_type(id_code['id'])
    rename_download(id_code['id'], mime_type)

    sys.exit(1)

    unpack_download(id_code['id'])
    content = load_data(f'{id_code["id"]}.xyz')
    print(content)


if __name__ == '__main__':
    main()
