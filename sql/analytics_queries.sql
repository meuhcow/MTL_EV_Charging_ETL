SELECT
    charging_level,
    COUNT(*) AS station_count
FROM charging_stations
GROUP BY charging_level
ORDER BY station_count DESC;

SELECT
    COALESCE(placement_type, 'unknown') AS placement_type,
    COUNT(*) AS station_count
FROM charging_stations
GROUP BY placement_type
ORDER BY station_count DESC;

SELECT
    site_id,
    site_name,
    address,
    station_count
FROM site_summary
ORDER BY station_count DESC, site_name
LIMIT 20;

SELECT
    station_id,
    latitude,
    longitude,
    geojson_latitude,
    geojson_longitude
FROM charging_stations
WHERE NOT coordinates_match_geojson;
