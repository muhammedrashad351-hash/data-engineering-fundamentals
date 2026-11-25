
from pathlib import Path
from urllib.request import urlopen
import shutil
import csv
import polars as pl


def extract_trips(source: Path, *, month: str, download: bool) -> pl.DataFrame:
    """Read a local Parquet file, downloading the requested month if allowed."""

    if not source.exists():

        if not download:
            raise FileNotFoundError(f"Parquet file not found: {source}")

        url = (
            "https://d37ci6vzurychx.cloudfront.net/trip-data/"
            f"yellow_tripdata_{month}.parquet"
        )

        source.parent.mkdir(parents=True, exist_ok=True)

        temporary_file = source.with_suffix(source.suffix + ".tmp")

        try:
            with urlopen(url, timeout=120) as response:
                with open(temporary_file, "wb") as file:
                    shutil.copyfileobj(response, file)

            temporary_file.replace(source)

        except Exception:
            if temporary_file.exists():
                temporary_file.unlink()
            raise

    return pl.read_parquet(source)

def extract_zones(source: Path) -> pl.DataFrame:
    """Read taxi-zone lookup data from a CSV file."""

    if not source.exists():
        raise FileNotFoundError(f"Zone CSV file not found: {source}")

    return pl.read_csv(
        source,
        schema_overrides={
            "LocationID": pl.Int64,
            "Borough": pl.String,
            "Zone": pl.String,
            "service_zone": pl.String,
        },
    ).rename({
        "LocationID": "location_id",
        "Borough": "borough",
        "Zone": "zone",
        "service_zone": "service_zone",
    })
