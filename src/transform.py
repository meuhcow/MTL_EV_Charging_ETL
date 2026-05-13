from __future__ import annotations

import json
import re

import pandas as pd

from src.config import RAW_CSV_PATH, RAW_GEOJSON_PATH


COLUMN_MAP = {
    "NOM_BORNE_RECHARGE": "station_id",
    "NOM_PARC": "site_name",
    "ADRESSE": "address",
    "VILLE": "city",
    "PROVINCE": "province",
    "NIVEAU_RECHARGE": "charging_level",
    "MODE_TARIFICATION": "pricing_mode",
    "TYPE_EMPLACEMENT": "placement_type",
    "LONGITUDE": "longitude",
    "LATITUDE": "latitude",
}


def _clean_text(value: object) -> object:
    if pd.isna(value):
        return value
    return re.sub(r"\s+", " ", str(value)).strip()


def _parse_site_id(site_name: object) -> object:
    if pd.isna(site_name):
        return None
    match = re.match(r"^(\d+)\s*\|", str(site_name))
    return match.group(1) if match else None


def _load_geojson_coordinates() -> pd.DataFrame:
    payload = json.loads(RAW_GEOJSON_PATH.read_text(encoding="utf-8"))
    rows = []
    for feature in payload.get("features", []):
        properties = feature.get("properties", {})
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates") or [None, None]
        rows.append(
            {
                "station_id": properties.get("NOM_BORNE_RECHARGE"),
                "geojson_longitude": coordinates[0],
                "geojson_latitude": coordinates[1],
            }
        )
    return pd.DataFrame(rows)


def transform() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV_PATH)
    df = df.rename(columns=COLUMN_MAP)
    df = df[list(COLUMN_MAP.values())]

    for column in ["station_id", "site_name", "address", "city", "province", "charging_level", "pricing_mode", "placement_type"]:
        df[column] = df[column].map(_clean_text)

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["site_id"] = df["site_name"].map(_parse_site_id)
    df["is_on_street"] = df["placement_type"].str.lower().eq("sur rue").fillna(False)
    df["coordinate_key"] = df["latitude"].round(6).astype(str) + "," + df["longitude"].round(6).astype(str)

    geojson_df = _load_geojson_coordinates()
    df = df.merge(geojson_df, on="station_id", how="left")
    df["coordinates_match_geojson"] = (
        df["longitude"].round(6).eq(df["geojson_longitude"].round(6))
        & df["latitude"].round(6).eq(df["geojson_latitude"].round(6))
    )

    return df.sort_values("station_id").reset_index(drop=True)
