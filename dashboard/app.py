from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
PARQUET_PATH = BASE_DIR / "data" / "processed" / "charging_stations.parquet"
QUALITY_REPORT_PATH = BASE_DIR / "reports" / "data_quality_report.json"


st.set_page_config(
    page_title="Montreal EV Charging Dashboard",
    page_icon="⚡",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    if not PARQUET_PATH.exists():
        st.error("Processed Parquet file not found. Run `make pipeline` first.")
        st.stop()
    df = pd.read_parquet(PARQUET_PATH)
    for column in ["charging_level", "placement_type", "pricing_mode"]:
        df[column] = df[column].fillna("Unknown")
    return df


def format_percent(value: float) -> str:
    return f"{value:.1%}"


df = load_data()

st.title("Montreal Public EV Charging Network")
st.caption("Portfolio dashboard powered by a Python ETL pipeline, Parquet, and DuckDB-ready analytics data.")

with st.sidebar:
    st.header("Filters")
    charging_levels = sorted(df["charging_level"].dropna().unique())
    placement_types = sorted(df["placement_type"].dropna().unique())
    pricing_modes = sorted(df["pricing_mode"].dropna().unique())

    selected_levels = st.multiselect(
        "Charging level",
        charging_levels,
        default=charging_levels,
    )
    selected_placements = st.multiselect(
        "Placement type",
        placement_types,
        default=placement_types,
    )
    selected_pricing = st.multiselect(
        "Pricing mode",
        pricing_modes,
        default=pricing_modes,
    )
    min_site_count = st.slider("Minimum chargers per site", 1, 20, 1)

filtered = df[
    df["charging_level"].isin(selected_levels)
    & df["placement_type"].isin(selected_placements)
    & df["pricing_mode"].isin(selected_pricing)
].copy()

site_summary = (
    filtered.groupby(
        [
            "site_id",
            "site_name",
            "address",
            "city",
            "province",
            "charging_level",
            "pricing_mode",
            "placement_type",
            "is_on_street",
        ],
        dropna=False,
    )
    .agg(
        latitude=("latitude", "mean"),
        longitude=("longitude", "mean"),
        station_count=("station_id", "count"),
    )
    .reset_index()
)
site_summary = site_summary[site_summary["station_count"] >= min_site_count]

total_stations = len(filtered)
total_sites = site_summary["site_name"].nunique()
fast_chargers = int((filtered["charging_level"] == "BRCC").sum())
on_street = int(filtered["is_on_street"].sum())
on_street_share = on_street / total_stations if total_stations else 0

metric_cols = st.columns(4)
metric_cols[0].metric("Stations", f"{total_stations:,}")
metric_cols[1].metric("Sites", f"{total_sites:,}")
metric_cols[2].metric("Fast chargers", f"{fast_chargers:,}")
metric_cols[3].metric("On-street share", format_percent(on_street_share))

st.divider()

left_col, right_col = st.columns([1.1, 0.9], gap="large")

with left_col:
    st.subheader("Charging Stations Map")
    map_df = filtered[["latitude", "longitude", "station_id", "site_name", "charging_level"]].dropna()
    st.map(map_df, latitude="latitude", longitude="longitude", size=16)

with right_col:
    st.subheader("Network Mix")
    level_counts = filtered["charging_level"].value_counts().rename_axis("charging_level").reset_index(name="station_count")
    st.bar_chart(level_counts, x="charging_level", y="station_count", color="#1f77b4")

    placement_counts = (
        filtered["placement_type"]
        .value_counts()
        .rename_axis("placement_type")
        .reset_index(name="station_count")
    )
    st.bar_chart(placement_counts, x="placement_type", y="station_count", color="#ff7f0e")

st.divider()

top_left, top_right = st.columns(2, gap="large")

with top_left:
    st.subheader("Top Sites")
    top_sites = site_summary.sort_values(["station_count", "site_name"], ascending=[False, True]).head(15)
    st.dataframe(
        top_sites[["site_name", "address", "charging_level", "placement_type", "station_count"]],
        width="stretch",
        hide_index=True,
    )

with top_right:
    st.subheader("Pricing Modes")
    pricing_counts = (
        filtered["pricing_mode"]
        .value_counts()
        .rename_axis("pricing_mode")
        .reset_index(name="station_count")
    )
    st.dataframe(pricing_counts, width="stretch", hide_index=True)

st.divider()

st.subheader("Station-Level Data")
st.dataframe(
    filtered[
        [
            "station_id",
            "site_name",
            "address",
            "city",
            "charging_level",
            "pricing_mode",
            "placement_type",
            "latitude",
            "longitude",
        ]
    ],
    width="stretch",
    hide_index=True,
)
