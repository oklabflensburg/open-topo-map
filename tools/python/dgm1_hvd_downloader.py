import click
import httpx
import json

from multiprocessing import Pool
from fake_useragent import UserAgent
from pathlib import Path


def process_feature(feature, verbose, dst):
    ua = UserAgent()
    url = feature['properties']['link_data']
    if verbose:
        print(url)

    r = httpx.get(url, headers={'User-Agent': ua.random})

    if r.status_code == 200:
        filename = url.split('file=')[1].split('&')[0]
        file_path = Path(dst) / filename
        if verbose:
            print(file_path)

        with file_path.open('wb') as f:
            f.write(r.content)
    else:
        print(f"Failed to download {url}: {r.status_code}")


@click.command()
@click.option('--src', '-s', type=click.Path(exists=True), required=True, help='Path to the source GeoJSON file')
@click.option('--dst', '-d', type=click.Path(file_okay=False, writable=True), required=True, help='Directory to save downloaded files')
@click.option('--verbose', '-v', is_flag=True, help='Print more verbose output')
def main(src, dst, verbose):
    with open(src, 'r') as geojson_file:
        geojson_data = json.load(geojson_file)

    features = geojson_data.get('features', [])

    with Pool() as pool:
        pool.starmap(process_feature, [
                     (feature, verbose, dst) for feature in features])

if __name__ == '__main__':
    main()
