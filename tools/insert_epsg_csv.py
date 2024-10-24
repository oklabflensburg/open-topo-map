import os
import sys
import click
import binascii
import traceback
import logging as log
import psycopg2
import csv

from shapely import wkb
from shapely.geometry import Polygon
from pyproj import Transformer
from dotenv import load_dotenv
from pathlib import Path



# log uncaught exceptions
def log_exceptions(type, value, tb):
    for line in traceback.TracebackException(type, value, tb).format(chain=True):
        log.exception(line)

    log.exception(value)

    sys.__excepthook__(type, value, tb) # calls default excepthook


def connect_database(env_path):
    try:
        load_dotenv(dotenv_path=Path(env_path))

        conn = psycopg2.connect(
            database = os.getenv('DB_NAME'),
            password = os.getenv('DB_PASS'),
            user = os.getenv('DB_USER'),
            host = os.getenv('DB_HOST'),
            port = os.getenv('DB_PORT')
        )

        conn.autocommit = True

        log.info('connection to database established')

        return conn
    except Exception as e:
        log.error(e)

        sys.exit(1)


def insert_row(cur, row):
    crs = row['crs']
    range_min_x = int(row['range_min_x'])
    range_min_y = int(row['range_min_y'])
    range_max_x = int(row['range_max_x'])
    range_max_y = int(row['range_max_y'])
    width = int(row['width'])
    height = int(row['height'])
    undefined_values = int(row['undefined_values'])
    file_name = row['file_name']
    flags = row['errors'][2:]

    # Convert hex string to an integer, then format it as a binary string
    bit_string = bin(int(flags, 16))[2:]

    # Ensure the bit string length matches the expected length of the BIT column (if necessary)
    # For example, if the BIT column is defined as BIT(32), you might want to pad the string
    bit_string_padded = bit_string.zfill(32)  # Adjust '32' to the length of your BIT column

    points = [(range_min_x, range_min_y), (range_max_x, range_min_y), (range_max_x, range_max_y), (range_min_x, range_max_y)]

    transformer = Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)
    transformed_points = list(transformer.itransform(points))

    polygon = Polygon(transformed_points)
    wkb_geometry = wkb.dumps(polygon, hex=True, srid=4326)

    sql = '''
        INSERT INTO sh_dgm1_meta 
            (crs, range_min_x, range_min_y, range_max_x, range_max_y, 
            width, height, undefined_values, file_name, flags, wkb_geometry)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    '''

    try:
        cur.execute(sql, (crs, range_min_x, range_min_y, range_max_x, range_max_y, 
            width, height, undefined_values, file_name, bit_string_padded, wkb_geometry))

        last_inserted_id = cur.fetchone()[0]

        log.info(f'inserted {file_name} with id {last_inserted_id}')
    except Exception as e:
        log.error(e)


def read_csv(conn, src):
    cur = conn.cursor()

    with open(src, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
    
        for row in reader:
            insert_row(cur, row)


@click.command()
@click.option('--env', '-e', type=str, required=True, help='Set your local dot env path')
@click.option('--src', '-s', type=click.Path(exists=True), required=True, help='Set src path to your csv')
@click.option('--verbose', '-v', is_flag=True, help='Print more verbose output')
@click.option('--debug', '-d', is_flag=True, help='Print detailed debug output')
def main(env, src, verbose, debug):
    if debug:
        log.basicConfig(format='%(levelname)s: %(message)s', level=log.DEBUG)
    if verbose:
        log.basicConfig(format='%(levelname)s: %(message)s', level=log.INFO)
        log.info(f'set logging level to verbose')
    else:
        log.basicConfig(format='%(levelname)s: %(message)s')

    recursion_limit = sys.getrecursionlimit()
    log.info(f'your system recursion limit: {recursion_limit}')

    conn = connect_database(env)
    data = read_csv(conn, Path(src))


if __name__ == '__main__':
    sys.excepthook = log_exceptions

    main()
