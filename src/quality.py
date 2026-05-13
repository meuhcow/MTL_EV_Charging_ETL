from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "station_id",
    "site_name",
    "address",
    "city",
    "province",
    "charging_level",
    "pricing_mode",
    "placement_type",
    "longitude",
    "latitude",
}


def validate_charging_stations(df: pd.DataFrame, report_path: Path) -> dict:
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))
    duplicate_station_ids = int(df["station_id"].duplicated().sum()) if "station_id" in df else None
    null_station_ids = int(df["station_id"].isna().sum()) if "station_id" in df else None
    invalid_latitudes = int((~df["latitude"].between(45.0, 46.0)).sum()) if "latitude" in df else None
    invalid_longitudes = int((~df["longitude"].between(-74.5, -73.0)).sum()) if "longitude" in df else None

    report = {
        "row_count": int(len(df)),
        "missing_columns": missing_columns,
        "duplicate_station_ids": duplicate_station_ids,
        "null_station_ids": null_station_ids,
        "invalid_latitudes": invalid_latitudes,
        "invalid_longitudes": invalid_longitudes,
        "passed": not missing_columns
        and duplicate_station_ids == 0
        and null_station_ids == 0
        and invalid_latitudes == 0
        and invalid_longitudes == 0,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
