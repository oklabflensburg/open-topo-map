#!./venv/bin/python

import time
import httpx
import pathlib
import shutil
import magic


def save_download(id_code, data):
    pathlib.Path('./tmp').mkdir(parents=True, exist_ok=True) 

    with open(f'./tmp/{id_code}', 'wb') as f:
        f.write(data)


def mime_type(id_code):
    mime = magic.from_file(f'./tmp/{id_code}', mime=True)

    return mime


def data_download(url):
    r = httpx.get(url)

    if r.status_code == httpx.codes.OK:
        return r.content

    return None


def job_request(id_code):
    time_stamp = int(time.time())
    headers = {'Content-Type': 'application/json'}
    url = f'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/multi.php?action=status&job={id_code}&_={time_stamp}'

    r = httpx.get(url, headers=headers)
    
    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def dgm_request(dgm_code):
    time_stamp = int(time.time())
    headers = {'Content-Type': 'application/json'}
    url = f'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/multi.php?url={dgm_code}.xyz&buttonClass=file1&id=6688&type=dgm1&action=start&_={time_stamp}'

    r = httpx.get(url, headers=headers)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def tile_request():
    headers = {'Content-Type': 'application/json'}
    url = 'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/_ajax/details.php?title=325286075&kachelname=dgm1_32_528_6075_1_sh&filepath=32520_6070&hoehenbezu=DE_DHHN92_NH&quasigeoid=DE_AdV_GCG2005_QGH&e_datum=2007-03-25&a_datum=2007-03-25&e_datum_dmy=25.03.2007&a_datum_dmy=25.03.2007&jahr=2007&ogc_fid=6688&type=dgm1&id=6688&_uid=dgm16688'

    r = httpx.get(url, headers=headers)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def main():
    dgm_code = tile_request()
    print(dgm_code)
    
    id_code = dgm_request(dgm_code['object']['kachelname'])
    print(id_code)
    
    job_status = job_request(id_code['id'])
    print(job_status)

    while job_status['status'] != 'done':
        time.sleep(1)
        job_status = job_request(id_code['id'])
        print(job_status)


    data = data_download(job_status['downloadUrl'])
    save_download(id_code['id'], data)

    mime = mime_type(id_code['id'])

    print(mime)


if __name__ == '__main__':
    main()
