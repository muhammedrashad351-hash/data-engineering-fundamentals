
import polars as pl


def clean_trips(source: pl.DataFrame) -> pl.DataFrame:
    """Clean taxi trips and return columns that match the database table."""

    trips = source.select(
        pl.col("VendorID").cast(pl.Int32, strict=False).alias("vendor_id"),
        pl.col("tpep_pickup_datetime")
        .cast(pl.Datetime("us"), strict=False)
        .alias("pickup_datetime"),
        pl.col("tpep_dropoff_datetime")
        .cast(pl.Datetime("us"), strict=False)
        .alias("dropoff_datetime"),
        pl.col("passenger_count").cast(pl.Int32, strict=False),
        pl.col("trip_distance").cast(pl.Float64, strict=False),
        pl.col("PULocationID").cast(pl.Int32, strict=False).alias("pickup_location_id"),
        pl.col("DOLocationID").cast(pl.Int32, strict=False).alias("dropoff_location_id"),
        pl.col("payment_type").cast(pl.Int32, strict=False),
        pl.col("fare_amount")
        .cast(pl.Float64, strict=False)
        .round(2)
        .cast(pl.Decimal(precision=12, scale=2), strict=False),
        pl.col("tip_amount")
        .cast(pl.Float64, strict=False)
        .round(2)
        .cast(pl.Decimal(precision=12, scale=2), strict=False),
        pl.col("total_amount")
        .cast(pl.Float64, strict=False)
        .round(2)
        .cast(pl.Decimal(precision=12, scale=2), strict=False),
    )

    trips = trips.filter(
        pl.col("pickup_datetime").is_not_null()
        & pl.col("dropoff_datetime").is_not_null()
        & (pl.col("dropoff_datetime") >= pl.col("pickup_datetime"))
        & (pl.col("trip_distance").is_null() | (pl.col("trip_distance") >= 0))
    )

    return trips
