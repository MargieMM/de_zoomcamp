from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket


@task(log_prints=True)
def fetch(dataset_url:str) -> pd.DataFrame:
    """Read taxi data from web to pandas DataFrame"""
    df = pd.read_csv(dataset_url)
    return df

@task(log_prints=True)
def clean(df = pd.DataFrame) -> pd.DataFrame:
    """Fix dtype issues"""
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"rows: {len(df)}")
    return df

@task()
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """ Write Dataframe out as a parquet file"""

    path= Path(f"data/{color}/{dataset_file}.parquet")
    df.to_parquet(path,compression="gzip")
    return path

@task()
def write_gcs(path:Path) -> None:
    """Uploading Local Parquet file to google cloud storage"""
    gcs_block = GcsBucket.load("zoom-gcs")
    path=Path(path).as_posix()
    gcs_block.upload_from_path(
        from_path=f"{path}", to_path=path)
    return

@flow(log_prints=True)
def etl_web_to_gcs() -> None:
    """This is the main ETL Function """
    color = "yellow"
    year = "2021"
    month = 1
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    df = fetch(dataset_url)
    df_clean = clean(df)
    path = write_local(df_clean, color, dataset_file)
    write_gcs(path)

if __name__ == '__main__':
    etl_web_to_gcs()