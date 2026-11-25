from datetime import datetime
from decimal import Decimal

import polars as pl

from transform import clean_trips


def test_cleaning_keeps_adjustments_nulls_and_unknown_locations():
    start = datetime(2024, 1, 2, 12)
    end = datetime(2024, 1, 2, 12, 15)
    source = pl.DataFrame(
        {
            "VendorID": [1] * 5,
            "tpep_pickup_datetime": [start, start, start, None, start],
            "tpep_dropoff_datetime": [end, end, end, end, start.replace(hour=11)],
            "passenger_count": [None, 1, 1, 1, 1],
            "trip_distance": [0.0, None, -2.0, 2.0, 2.0],
            "PULocationID": [999, 1, 1, 1, 1],
            "DOLocationID": [1] * 5,
            "payment_type": [1] * 5,
            "fare_amount": [-1.23, 2.37, 8.25, 10.0, 9.0],
            "tip_amount": [None, 0.20, 1.0, 1.0, 1.0],
            "total_amount": [-1.23, 2.57, 9.25, 11.0, 10.0],
        }
    )

    trips = clean_trips(source)

    assert trips.height == 2
    assert trips["pickup_datetime"].to_list() == [start, start]
    assert trips["pickup_location_id"].to_list() == [999, 1]
    assert trips["passenger_count"].to_list() == [None, 1]
    assert trips["trip_distance"].to_list() == [0.0, None]
    assert trips["fare_amount"].to_list() == [Decimal("-1.23"), Decimal("2.37")]
    assert trips["tip_amount"].to_list() == [None, Decimal("0.20")]
