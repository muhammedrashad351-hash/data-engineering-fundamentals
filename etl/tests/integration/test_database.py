
from datetime import datetime
from decimal import Decimal

import polars as pl
import psycopg

from load import load_trips, load_zones


def test_trip_and_zone_tables_and_transaction_rollback():
    with psycopg.connect(connect_timeout=5, autocommit=True) as conn:
        assert conn.execute("SELECT 1").fetchone() == (1,)

        columns = conn.execute(
            """
            SELECT column_name, data_type, is_nullable, is_identity
            FROM information_schema.columns
            WHERE table_schema = 'raw'
              AND table_name = 'yellow_taxi_trips'
            ORDER BY ordinal_position
            """
        ).fetchall()

        assert columns == [
            ("trip_id", "bigint", "NO", "YES"),
            ("vendor_id", "integer", "YES", "NO"),
            ("pickup_datetime", "timestamp without time zone", "NO", "NO"),
            ("dropoff_datetime", "timestamp without time zone", "NO", "NO"),
            ("passenger_count", "integer", "YES", "NO"),
            ("trip_distance", "double precision", "YES", "NO"),
            ("pickup_location_id", "integer", "YES", "NO"),
            ("dropoff_location_id", "integer", "YES", "NO"),
            ("payment_type", "integer", "YES", "NO"),
            ("fare_amount", "numeric", "YES", "NO"),
            ("tip_amount", "numeric", "YES", "NO"),
            ("total_amount", "numeric", "YES", "NO"),
        ]

        with conn.transaction(force_rollback=True):
            inserted = conn.execute(
                """
                INSERT INTO raw.yellow_taxi_trips
                    (pickup_datetime, dropoff_datetime, pickup_location_id, fare_amount)
                VALUES ('2024-01-01 09:00:00', '2024-01-01 09:05:00', 999, %s)
                RETURNING trip_id, passenger_count, fare_amount
                """,
                (Decimal("-1.23"),),
            ).fetchone()

            trip_id, passenger_count, fare = inserted
            assert trip_id > 0
            assert passenger_count is None
            assert fare == Decimal("-1.23")

        assert conn.execute(
            "SELECT trip_id FROM raw.yellow_taxi_trips WHERE trip_id = %s",
            (trip_id,),
        ).fetchone() is None


def test_copy_appends_trips_and_rolls_back():
    trips = pl.DataFrame({
        "vendor_id": [1],
        "pickup_datetime": [datetime(2024, 1, 1, 9, 0)],
        "dropoff_datetime": [datetime(2024, 1, 1, 9, 5)],
        "passenger_count": [1],
        "trip_distance": [1.2],
        "pickup_location_id": [999],
        "dropoff_location_id": [999],
        "payment_type": [1],
        "fare_amount": [10.0],
        "tip_amount": [2.0],
        "total_amount": [12.0],
    })

    with psycopg.connect(connect_timeout=5) as conn:
        initial_count = conn.execute(
            "SELECT count(*) FROM raw.yellow_taxi_trips"
        ).fetchone()[0]

        with conn.transaction(force_rollback=True):
            assert load_trips(conn, trips) == 1
            assert load_trips(conn, trips) == 1

            current_count = conn.execute(
                "SELECT count(*) FROM raw.yellow_taxi_trips"
            ).fetchone()[0]

            assert current_count == initial_count + 2

        final_count = conn.execute(
            "SELECT count(*) FROM raw.yellow_taxi_trips"
        ).fetchone()[0]

        assert final_count == initial_count


def test_repeated_zone_load_does_not_duplicate_location():
    zones = pl.DataFrame({
        "location_id": [999999],
        "borough": ["Test Borough"],
        "zone": ["Test Zone"],
        "service_zone": ["Test Service"],
    })

    with psycopg.connect(connect_timeout=5, autocommit=True) as conn:
        try:
            with conn.transaction():
                assert load_zones(conn, zones) == 1

            with conn.transaction():
                assert load_zones(conn, zones) == 1

            result = conn.execute(
                """
                SELECT count(*)
                FROM raw.taxi_zones
                WHERE location_id = 999999
                """
            ).fetchone()[0]

            assert result == 1

        finally:
            conn.execute(
                "DELETE FROM raw.taxi_zones WHERE location_id = 999999"
            )
