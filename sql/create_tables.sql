CREATE OR REPLACE TABLE charging_stations AS
SELECT *
FROM read_parquet('data/processed/charging_stations.parquet');

CREATE OR REPLACE VIEW site_summary AS
SELECT
    site_id,
    site_name,
    address,
    city,
    province,
    charging_level,
    pricing_mode,
    placement_type,
    is_on_street,
    AVG(latitude) AS latitude,
    AVG(longitude) AS longitude,
    COUNT(*) AS station_count
FROM charging_stations
GROUP BY ALL;
