from __future__ import annotations

import duckdb

from src.config import DUCKDB_PATH, REPORTS_DIR


QUERIES = {
    "stations_by_charging_level.csv": """
        SELECT
            charging_level,
            COUNT(*) AS station_count
        FROM charging_stations
        GROUP BY charging_level
        ORDER BY station_count DESC
    """,
    "stations_by_placement_type.csv": """
        SELECT
            COALESCE(placement_type, 'unknown') AS placement_type,
            COUNT(*) AS station_count
        FROM charging_stations
        GROUP BY placement_type
        ORDER BY station_count DESC
    """,
    "top_sites_by_station_count.csv": """
        SELECT
            site_id,
            site_name,
            address,
            station_count
        FROM site_summary
        ORDER BY station_count DESC, site_name
        LIMIT 20
    """,
    "quality_coordinate_mismatches.csv": """
        SELECT
            station_id,
            latitude,
            longitude,
            geojson_latitude,
            geojson_longitude
        FROM charging_stations
        WHERE NOT coordinates_match_geojson
    """,
}


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DUCKDB_PATH)) as con:
        for file_name, query in QUERIES.items():
            output_path = REPORTS_DIR / file_name
            con.execute(f"COPY ({query}) TO ? WITH (HEADER, DELIMITER ',')", [str(output_path)])
            print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
