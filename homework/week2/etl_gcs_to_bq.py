from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect.tasks import task_input_hash
from datetime import timedelta
from prefect_gcp import GcpCredentials

# @task(log_prints=True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
# Code above needed when using prefect build apply
@task(log_prints=True, retries=3,cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def fetch(dataset_url:str) -> pd.DataFrame:
    """Read taxi data from web to pandas DataFrame"""
    df = pd.read_csv(dataset_url)
    print(f"Finished Fetching the data from URL")
    return df

@task(log_prints=True,cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """ Write Dataframe out as a parquet file"""
    path= Path(f"data/{color}/{dataset_file}.parquet")
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)
    df.to_parquet(path,compression="gzip")
    print(f"Finished Writing to local: {path}")
    return path

@task(log_prints=True,cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def write_gcs(path:Path) ->pd.DataFrame:
    """Uploading Local Parquet file to google cloud storage"""
    gcs_block = GcsBucket.load("zoom-gcs")
    path=Path(path).as_posix()
    gcs_block.upload_from_path(from_path=f"{path}", to_path=path)
    print(f"Finished Uploading to GCS {path}")
    return path

@task(log_prints=True)
def read_from_gcs(path:Path) -> None:
    """ Read Data from GCS"""
    gcs_block=GcsBucket.load("zoom-gcs")
    gcs_block.get_directory(from_path=path, local_path=f"{path}")
    df = pd.read_parquet(path)
    print(f"Finished Reading the data from GCS")
    return df

@task(log_prints=True)
def write_bq(df:pd.DataFrame)-> None:
    """ Write DataFrame to BigQuery"""
    gcp_credentials_block=GcpCredentials.load("zoom-gcp-creds")
    df.to_gbq(
        destination_table="dezoomcamp.rides",
        project_id="platinum-tube-375819",
        credentials= gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append"
    )

@flow(log_prints=True)
def etl_gcs_to_bq(year:int, month: int, color:str) -> None:
    """This is the main ETL Function with parameters """
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    df = fetch(dataset_url)
    path = write_local(df, color, dataset_file)
    write_gcs(path)
    df_read=read_from_gcs(path)
    write_bq(df_read)

@flow()
def etl_parent_flow(months: list[int] = [3], year: int = 2019, color: str = "yellow" ):
    for month in months:
        etl_gcs_to_bq(year, month, color)

if __name__ == '__main__':
    color = "yellow"
    months = [3]
    year = 2019
    etl_parent_flow(months, year, color)