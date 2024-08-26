import os
import sys
import time
import click
import httpx
import magic

from fake_useragent import UserAgent
from pathlib import Path



def save_download(download_path, data):
    directories = Path(download_path).parent.resolve()
    Path(directories).mkdir(parents=True, exist_ok=True)

    with open(download_path, 'wb') as f:
        f.write(data)

    print(f'saved archieve to {download_path}')


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


def job_request(tile_id, tile_flur, user_agent):
    time_stamp = int(time.time())
    headers = {'Content-Type': 'application/json', 'User-Agent': user_agent}
    url = f'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/multi.php?url={tile_flur}.xml.gz&buttonClass=file1&id={tile_id}&type=alkis&action=start&_={time_stamp}'
    print(url)

    r = httpx.get(url, headers=headers, verify=False)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def tile_request(tile_id, user_agent):
    headers = {'Content-Type': 'application/json', 'User-Agent': user_agent}
    url = f'https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/_ajax/details.php?type=alkis&id={tile_id}'
    print(url)

    r = httpx.get(url, headers=headers, verify=False)

    if r.status_code == httpx.codes.OK:
        return r.json()

    return {}


def fetch_data(tile_id, path, verbose):
    ua = UserAgent()
    user_agent = ua.random

    response_tile = tile_request(tile_id, user_agent)
    print(response_tile)
    tile_flur = response_tile['object']['flur']

    response_job = job_request(tile_id, tile_flur, user_agent)
    print(response_job)
    job_id = response_job['id']

    reponse_status = status_request(job_id, user_agent)
    print(reponse_status)

    while reponse_status['status'] != 'done':
        time.sleep(1)
        reponse_status = status_request(job_id, user_agent)
        print(reponse_status)

    data = download_archive(reponse_status['downloadUrl'])
    file_name = f'{tile_id}_{tile_flur}'

    if Path(path).is_dir():
        download_path = Path(f'{path}/sh/alkis/{file_name}.zip')
    else:
        download_path = Path(f'../data/sh/alkis/{file_name}.zip')

    save_download(download_path, data)

    return


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Print more verbose output')
@click.option('--path', '-p', type=str, help='Set the source output format')
@click.argument('start', type=int, nargs=1)
@click.argument('end', type=int, nargs=1)
def main(start, end, path, verbose):
    if not start <= end:
        print('Error: start must be greater or equal to end')
        sys.exit(1)

    for tile_id in range(start, end):
        fetch_data(tile_id, path, verbose)


if __name__ == '__main__':
    main()
