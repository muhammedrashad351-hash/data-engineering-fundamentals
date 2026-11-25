BEGIN;

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.yellow_taxi_trips (
    trip_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vendor_id integer,
    pickup_datetime timestamp without time zone NOT NULL,
    dropoff_datetime timestamp without time zone NOT NULL,
    passenger_count integer,
    trip_distance double precision,
    pickup_location_id integer,
    dropoff_location_id integer,
    payment_type integer,
    fare_amount numeric(14, 2),
    tip_amount numeric(14, 2),
    total_amount numeric(14, 2)
);

CREATE TABLE IF NOT EXISTS raw.taxi_zones (
    location_id integer PRIMARY KEY,
    borough text NOT NULL,
    zone text NOT NULL,
    service_zone text
);

COMMIT;
