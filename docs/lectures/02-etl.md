# Lecture 02 · Data ingestion and ETL

## Objectives

- Explain how extract, transform and load differ from extract, load and transform.
- Inspect a Parquet schema and translate source fields to a SQL contract.
- Append one month of cleaned Yellow Taxi trips to PostgreSQL and verify the load.

## Architecture and prerequisites

NYC TLC → local Parquet → Polars → Psycopg → PostgreSQL `raw` tables.
The taxi zone CSV supplies reference rows for later analysis.

Use the Python, uv and PostgreSQL tools listed in [setup](../setup.md). Follow
that guide to configure `.env`, sync the project and initialize the tables.
Read the [dataset contract](../datasets.md) before implementing the cleaning rules.

## Tasks

1. In `extract.py`, open the specified local Parquet file or download the
   requested TLC month when the default file is missing. Use a timeout and
   publish only a completed download. Read the result with Polars.
2. In `transform.py`, select and rename the required fields, cast them and
   apply the documented cleaning rules. Retain nullable values and fare adjustments.
3. In `load.py`, append accepted trips in a database transaction. Use an
   ordinary insert or PostgreSQL `COPY`. Load taxi zones once, keyed by location ID.
4. In `pipeline.py`, report the source, accepted and loaded row counts and elapsed
   time. Confirm the number of appended rows with SQL.

## Run and verify

Run these commands from `etl/`.

```sh
uv run --locked python pipeline.py --help
uv run --locked python -m pytest -q
uv run --locked --env-file ../.env -- python -m pytest -q tests/integration
uv run --locked python -m pytest -q tests/acceptance
uv run --locked --env-file ../.env -- python pipeline.py
```

The default tests and isolated PostgreSQL integration test should pass. The
acceptance test and default pipeline command intentionally fail at the
unfinished transform and extract steps respectively. For local experimentation,
use `--source /path/to/fixture.parquet`. Use a separate disposable database
for repeated test loads.

After implementing the tasks, the pipeline should print counts and an elapsed
time. Verify with `uv run --locked --env-file ../.env -- psql -X` from
`etl/`, then run these queries.

```sql
SELECT count(*) AS loaded,
       min(pickup_datetime) AS first_pickup,
       max(pickup_datetime) AS last_pickup
FROM raw.yellow_taxi_trips;

SELECT trip_id, pickup_datetime, pickup_location_id, fare_amount
FROM raw.yellow_taxi_trips ORDER BY trip_id LIMIT 5;

SELECT count(*) AS invalid
FROM raw.yellow_taxi_trips
WHERE dropoff_datetime < pickup_datetime OR trip_distance < 0;

SELECT count(*) AS zones FROM raw.taxi_zones;
```

## Acceptance and limitations

The fixture should retain both valid rows and their documented null and money
values. On a fresh database, the real-month table count must equal the number
of accepted records, and invalid rows must be zero. On a database with
existing trips, compare the change in count. A repeated trip load appends the
same input again, so practice reruns with a disposable fixture database.

In Lecture 03, dbt will turn these raw tables into a dimensional model and daily
pickup-borough report.
