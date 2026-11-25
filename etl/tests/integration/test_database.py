from decimal import Decimal

import psycopg


def test_trip_and_zone_tables_and_transaction_rollback():
    with psycopg.connect(connect_timeout=5, autocommit=True) as conn:
        assert conn.execute("SELECT 1").fetchone() == (1,)
        columns = conn.execute(
            """
            SELECT column_name, data_type, is_nullable, is_identity
            FROM information_schema.columns
            WHERE table_schema = 'raw' AND table_name = 'yellow_taxi_trips'
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
        assert conn.execute(
            "SELECT location_id, borough, zone, service_zone FROM raw.taxi_zones LIMIT 0"
        ).fetchall() == []

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
            "SELECT trip_id FROM raw.yellow_taxi_trips WHERE trip_id = %s", (trip_id,)
        ).fetchone() is None
