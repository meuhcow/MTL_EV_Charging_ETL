from __future__ import annotations

import duckdb
import pandas as pd

from src.config import ANALYTICS_SUMMARY_PATH, DUCKDB_PATH, PROCESSED_PARQUET_PATH


def write_parquet(df: pd.DataFrame) -> None:
    PROCESSED_PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_PARQUET_PATH, engine="pyarrow", index=False)


def load_duckdb() -> None:
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DUCKDB_PATH)) as con:
        con.execute("DROP TABLE IF EXISTS charging_stations")
        con.execute(
            """
            CREATE TABLE charging_stations AS
            SELECT *
            FROM read_parquet(?)
            """,
            [str(PROCESSED_PARQUET_PATH)],
        )
        con.execute("DROP VIEW IF EXISTS site_summary")
        con.execute(
            """
            CREATE VIEW site_summary AS
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
            GROUP BY ALL
            """
        )


def write_analytics_summary() -> None:
    ANALYTICS_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DUCKDB_PATH)) as con:
        summary = con.execute(
            """
            SELECT 'total_stations' AS metric, COUNT(*)::VARCHAR AS value FROM charging_stations
            UNION ALL
            SELECT 'total_sites', COUNT(DISTINCT site_id)::VARCHAR FROM charging_stations
            UNION ALL
            SELECT 'on_street_stations', COUNT(*)::VARCHAR FROM charging_stations WHERE is_on_street
            UNION ALL
            SELECT 'charging_levels', COUNT(DISTINCT charging_level)::VARCHAR FROM charging_stations
            """
        ).fetchdf()
    summary.to_csv(ANALYTICS_SUMMARY_PATH, index=False)
