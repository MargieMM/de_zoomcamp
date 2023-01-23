import os
import argparse

from time import time

import pandas as pd
from sqlalchemy import create_engine


def main(params):
    user = params.user
    password = params.password
    host = params.host 
    port = params.port 
    db = params.db
    table_name = params.table_name
    url = 'https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv'

    os.system(f"wget {url} -O taxi+_zone_lookup.csv")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_zones = pd.read_csv('taxi+_zone_lookup.csv')

    engine.connect()
    
    df_zones.to_sql(name=table_name, con=engine, if_exists='replace')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest Lookup data to Postgres')

    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')

    args = parser.parse_args()

    main(args)