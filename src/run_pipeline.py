from __future__ import annotations

from src.config import PROCESSED_PARQUET_PATH, QUALITY_REPORT_PATH
from src.ingest import ingest
from src.load import load_duckdb, write_analytics_summary, write_parquet
from src.quality import validate_charging_stations
from src.transform import transform


def main() -> None:
    print("Starting Montreal EV charging data pipeline")
    ingest()
    df = transform()
    report = validate_charging_stations(df, QUALITY_REPORT_PATH)
    write_parquet(df)
    load_duckdb()
    write_analytics_summary()

    print(f"Rows processed: {len(df):,}")
    print(f"Quality checks passed: {report['passed']}")
    print(f"Parquet written to: {PROCESSED_PARQUET_PATH}")
    print("Pipeline complete")


if __name__ == "__main__":
    main()
