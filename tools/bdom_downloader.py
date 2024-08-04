import os
import sys
import time
import click
import httpx
import magic

from fake_useragent import UserAgent
from pathlib import Path



def save_download(download_path, data):
    Path('./sh').mkdir(parents=True, exist_ok=True)

    with open(download_path, 'wb') as f:
        f.write(data)


def get_mime_type(download_path):
    mime_type = magic.from_file(download_path, mime=True)

    return mime_type


def rename_download(download_path, archive_path):
    os.rename(download_path, archive_path)


def download_archive(url):
    r = httpx.get(url, verify=False)

    if r.status_code == httpx.codes.OK:
        return r.content

    return None


def status_request(id_code, user_agent):
    time_stamp = int(time.time())
    headers = {'Content-Type': 'application/json', 'User-Agent': user_agent}
    url = f'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/multi.php?action=status&job={id_code}&_={time_stamp}'
    print(url)

    r = httpx.get(url, headers=headers, verify=False)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def job_request(tile_year, tile_bdom, tile_path, tile_id, user_agent):
    time_stamp = int(time.time())
    headers = {'Content-Type': 'application/json', 'User-Agent': user_agent}
    url = f'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/multi.php?url=/data/geodaten/sh/bDOM/bDOM_{tile_year}/{tile_bdom}/{tile_path}/&buttonClass=ebenen&id={tile_id}&type=bdom&action=start&_={time_stamp}'
    print(url)

    r = httpx.get(url, headers=headers, verify=False)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def tile_request(tile_id, user_agent):
    headers = {'Content-Type': 'application/json', 'User-Agent': user_agent}
    url = f'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/_ajax/details.php?type=bdom&id={tile_id}&_uid=bdom{tile_id}'
    print(url)

    r = httpx.get(url, headers=headers, verify=False)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def fetch_data(tile_id, unpack, verbose):
    ua = UserAgent()
    user_agent = ua.random

    response_tile = tile_request(tile_id, user_agent)
    print(response_tile)
    tile_name = response_tile['object']['kachel_n']
    tile_bdom = response_tile['object']['kach10km']
    tile_path = response_tile['object']['filepath']
    tile_year = response_tile['object']['jahr']

    response_job = job_request(tile_year, tile_bdom, tile_path, tile_id, user_agent)
    print(response_job)
    job_id = response_job['id']

    reponse_status = status_request(job_id, user_agent)
    print(reponse_status)

    while reponse_status['status'] != 'done':
        time.sleep(1)
        reponse_status = status_request(job_id, user_agent)
        print(reponse_status)

    data = download_archive(reponse_status['downloadUrl'])
    file_name = f'{tile_id}_{tile_name}'
    download_path = Path(f'./sh/{file_name}')

    save_download(download_path, data)
    mime_type = get_mime_type(download_path)
    file_type = mime_type.split('/')

    if len(file_type) == 0:
        print('Error: no file extension detected')
        sys.exit(1)

    file_extension = file_type[-1]
    archive_path = Path(f'./sh/{file_name}.{file_extension}')
    target_path = Path(f'./sh/{file_name}')
    content_path = Path(f'./sh/{file_name}/{tile_name}.xyz')

    rename_download(download_path, archive_path)


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Print more verbose output')
@click.option('--unpack', '-u', is_flag=True, help='Unpack downloaded archive')
@click.argument('start', type=int, nargs=1)
@click.argument('end', type=int, nargs=1)
def main(start, end, unpack, verbose):
    if not start <= end:
        print('Error: start must be greater or equal to end')
        sys.exit(1)

    for tile_id in range(start, end):
        print(tile_id)
        fetch_data(tile_id, unpack, verbose)


if __name__ == '__main__':
    main()
