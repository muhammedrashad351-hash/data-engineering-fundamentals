# Local data

| Directory | Contents |
| --- | --- |
| `raw/yellow_taxi/` | Unmodified TLC Yellow Taxi Parquet files, named `yellow_tripdata_YYYY-MM.parquet` |
| `raw/reference/` | The original `taxi_zone_lookup.csv` |

These directories are ignored apart from their placeholders. Keep downloaded
files and local test data out of Git. Set `TAXI_DATA_DIR` to an absolute
directory to keep another lecture or an isolated test separate. The default
data directory is relative to the location of the course checkout.
