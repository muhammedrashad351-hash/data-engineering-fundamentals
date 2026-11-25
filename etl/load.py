
import polars as pl
from psycopg import Connection


def load_trips(conn: Connection, trips: pl.DataFrame) -> int:
    """Append accepted trips and return the number written."""

    columns = [
        "vendor_id",
        "pickup_datetime",
        "dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "pickup_location_id",
        "dropoff_location_id",
        "payment_type",
        "fare_amount",
        "tip_amount",
        "total_amount",
    ]

    trips = trips.select(columns)

    with conn.cursor() as cursor:
        with cursor.copy(
            """
            COPY raw.yellow_taxi_trips (
                vendor_id,
                pickup_datetime,
                dropoff_datetime,
                passenger_count,
                trip_distance,
                pickup_location_id,
                dropoff_location_id,
                payment_type,
                fare_amount,
                tip_amount,
                total_amount
            ) FROM STDIN
            """
        ) as copy:
            for row in trips.iter_rows():
                copy.write_row(row)

    return trips.height
def load_zones(conn: Connection, zones: pl.DataFrame) -> int:
    """Load taxi zones, updating existing location records safely."""

    columns = ["location_id", "borough", "zone", "service_zone"]
    zones = zones.select(columns)

    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TEMP TABLE staging_taxi_zones (
                location_id integer PRIMARY KEY,
                borough text NOT NULL,
                zone text NOT NULL,
                service_zone text
            ) ON COMMIT DROP
        """)

        with cursor.copy("""
            COPY staging_taxi_zones (
                location_id,
                borough,
                zone,
                service_zone
            ) FROM STDIN
        """) as copy:
            for row in zones.iter_rows():
                copy.write_row(row)

        cursor.execute("""
            INSERT INTO raw.taxi_zones (
                location_id,
                borough,
                zone,
                service_zone
            )
            SELECT
                location_id,
                borough,
                zone,
                service_zone
            FROM staging_taxi_zones
            ON CONFLICT (location_id)
            DO UPDATE SET
                borough = EXCLUDED.borough,
                zone = EXCLUDED.zone,
                service_zone = EXCLUDED.service_zone
        """)

    return zones.height
