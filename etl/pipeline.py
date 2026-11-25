
import argparse
import os
import sys
from datetime import date
from pathlib import Path
from time import perf_counter

import psycopg

from extract import extract_trips, extract_zones
from load import load_trips, load_zones
from transform import clean_trips

DEFAULT_MONTH = "2024-01"
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def parse_month(value: str) -> str:
    try:
        date.fromisoformat(f"{value}-01")
    except ValueError:
        raise argparse.ArgumentTypeError(
            "month must be in YYYY-MM format"
        ) from None
    return value


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append cleaned Yellow Taxi trips to PostgreSQL."
    )

    parser.add_argument("--month", type=parse_month, default=DEFAULT_MONTH)

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=os.environ.get("TAXI_DATA_DIR") or DEFAULT_DATA_DIR,
        help="absolute data directory",
    )

    parser.add_argument(
        "--source",
        type=Path,
        help="use a local Parquet file without downloading",
    )

    args = parser.parse_args(argv)

    if not args.data_dir.is_absolute():
        parser.error("the data directory must be an absolute path")

    args.download = args.source is None

    if args.download:
        args.source = (
            args.data_dir
            / "raw"
            / "yellow_taxi"
            / f"yellow_tripdata_{args.month}.parquet"
        )
    else:
        args.source = args.source.resolve()

    return args


def run(args: argparse.Namespace) -> None:
    start_time = perf_counter()

    zones_path = (
        args.data_dir
        / "raw"
        / "reference"
        / "taxi_zone_lookup.csv"
    )

    source_trips = extract_trips(
        args.source,
        month=args.month,
        download=args.download,
    )

    zones = extract_zones(zones_path)

    accepted_trips = clean_trips(source_trips)

    rejected_count = source_trips.height - accepted_trips.height

    # Both loads run in one database transaction.
    with psycopg.connect(connect_timeout=10) as conn:
        inserted_zones = load_zones(conn, zones)
        inserted_trips = load_trips(conn, accepted_trips)

    elapsed = perf_counter() - start_time

    print("\n========== ETL RESULTS ==========")
    print(f"Source trips:       {source_trips.height:,}")
    print(f"Accepted trips:     {accepted_trips.height:,}")
    print(f"Rejected trips:     {rejected_count:,}")
    print(f"Loaded trips:       {inserted_trips:,}")
    print(f"Source zones:       {zones.height:,}")
    print(f"Loaded/updated zones: {inserted_zones:,}")
    print(f"Elapsed time:       {elapsed:.2f} seconds")
    print("================================")


def main() -> int:
    try:
        run(parse_args())
    except (NotImplementedError, FileNotFoundError) as error:
        print(error, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
