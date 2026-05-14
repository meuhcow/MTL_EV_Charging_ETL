from __future__ import annotations

from pathlib import Path

import altair as alt
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


BASE_DIR = Path(__file__).resolve().parents[1]
PARQUET_PATH = BASE_DIR / "data" / "processed" / "charging_stations.parquet"


st.set_page_config(
    page_title="Montreal EV Charging Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    :root {
        --teal: #31cdbd;
        --teal-dark: #1da99c;
        --ink: #172033;
        --muted: #718096;
        --line: #e9eef5;
        --panel: #ffffff;
        --soft: #f7fafc;
    }

    .stApp {
        background: linear-gradient(180deg, #f8fbff 0%, #eef5fb 100%);
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1380px;
        padding-top: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }

    [data-testid="stToolbar"],
    .stDeployButton {
        display: none;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: var(--ink);
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: var(--ink);
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: #e6fffb;
        color: #107c72;
        border: 1px solid #b7f4eb;
        border-radius: 8px;
    }

    [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 18px 18px 14px;
        box-shadow: 0 14px 40px rgba(32, 64, 86, 0.08);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-weight: 800;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--line);
        border-radius: 8px;
        box-shadow: 0 14px 40px rgba(32, 64, 86, 0.06);
        background: var(--panel);
    }

    [data-testid="stVegaLiteChart"] {
        background: #ffffff;
        border-radius: 8px;
    }

    h1, h2, h3 {
        color: var(--ink);
        letter-spacing: 0;
    }

    .hero {
        position: relative;
        overflow: hidden;
        border-radius: 8px;
        padding: 34px 38px;
        margin: 8px 0 26px;
        min-height: 218px;
        color: white;
        background:
            linear-gradient(120deg, rgba(38, 203, 188, 0.98), rgba(44, 214, 200, 0.82)),
            radial-gradient(circle at 88% 20%, rgba(255, 255, 255, 0.40), transparent 26%);
        box-shadow: 0 20px 50px rgba(18, 150, 139, 0.25);
    }

    .hero::after {
        content: "";
        position: absolute;
        right: -80px;
        top: 26px;
        width: 56%;
        height: 220px;
        background: rgba(255, 255, 255, 0.72);
        transform: rotate(-7deg);
        border-radius: 8px;
        box-shadow: 0 24px 60px rgba(23, 32, 51, 0.18);
    }

    .hero-copy {
        position: relative;
        z-index: 2;
        max-width: 430px;
    }

    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 0;
        text-transform: uppercase;
        opacity: 0.96;
    }

    .hero-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.92);
        color: var(--teal-dark);
        font-weight: 900;
        font-size: 22px;
    }

    .hero h1 {
        margin: 18px 0 10px;
        color: #ffffff;
        font-size: 38px;
        line-height: 1.05;
        letter-spacing: 0;
    }

    .hero p {
        margin: 0;
        color: rgba(255, 255, 255, 0.92);
        font-size: 16px;
        line-height: 1.55;
    }

    .ev-scene {
        position: absolute;
        right: 56px;
        bottom: 30px;
        z-index: 3;
        width: 450px;
        height: 170px;
    }

    .ev-road {
        position: absolute;
        left: 12px;
        right: 8px;
        bottom: 4px;
        height: 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.38);
    }

    .ev-car {
        position: absolute;
        left: 18px;
        bottom: 32px;
        width: 288px;
        height: 74px;
        border-radius: 48px 72px 30px 30px;
        background: rgba(255, 255, 255, 0.94);
        box-shadow: 0 18px 38px rgba(23, 32, 51, 0.16);
    }

    .ev-car::before {
        content: "";
        position: absolute;
        left: 88px;
        top: -42px;
        width: 142px;
        height: 58px;
        border-radius: 80px 88px 10px 10px;
        background: rgba(255, 255, 255, 0.88);
        box-shadow: inset -48px 0 0 rgba(49, 205, 189, 0.14);
    }

    .ev-car::after {
        content: "";
        position: absolute;
        right: 90px;
        top: 28px;
        width: 44px;
        height: 26px;
        border-radius: 7px;
        background: rgba(49, 205, 189, 0.16);
    }

    .ev-wheel {
        position: absolute;
        bottom: -11px;
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: #172033;
        border: 9px solid rgba(231, 241, 247, 0.95);
    }

    .ev-wheel.left {
        left: 58px;
    }

    .ev-wheel.right {
        right: 56px;
    }

    .ev-port {
        position: absolute;
        right: 22px;
        top: 27px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #172033;
        box-shadow: 0 0 0 5px rgba(49, 205, 189, 0.16);
    }

    .ev-charger {
        position: absolute;
        right: 18px;
        bottom: 26px;
        width: 72px;
        height: 128px;
        border-radius: 16px;
        background: rgba(23, 32, 51, 0.92);
        box-shadow: 0 18px 38px rgba(23, 32, 51, 0.18);
    }

    .ev-charger::before {
        content: "";
        position: absolute;
        left: 17px;
        top: 18px;
        width: 38px;
        height: 28px;
        border-radius: 8px;
        background: rgba(49, 205, 189, 0.95);
    }

    .ev-charger::after {
        content: "EV";
        position: absolute;
        left: 18px;
        top: 62px;
        color: #ffffff;
        font-weight: 800;
        font-size: 18px;
    }

    .ev-cable {
        position: absolute;
        right: 88px;
        bottom: 80px;
        width: 84px;
        height: 42px;
        border-bottom: 8px solid rgba(23, 32, 51, 0.82);
        border-right: 8px solid rgba(23, 32, 51, 0.82);
        border-radius: 0 0 44px 0;
    }

    .section-title {
        margin: 10px 0 12px;
        color: var(--ink);
        font-size: 19px;
        font-weight: 800;
    }

    .subtle {
        color: var(--muted);
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 12px;
    }

    .pricing-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        margin-top: 4px;
    }

    .pricing-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 18px;
        box-shadow: 0 14px 36px rgba(32, 64, 86, 0.06);
    }

    .pricing-label {
        color: var(--muted);
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .pricing-value {
        color: var(--ink);
        font-size: 30px;
        line-height: 1;
        font-weight: 850;
    }

    @media (max-width: 1100px) {
        .ev-scene {
            display: none;
        }
        .hero::after {
            display: none;
        }
        .hero h1 {
            font-size: 34px;
        }
        .pricing-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    if not PARQUET_PATH.exists():
        st.error("Processed Parquet file not found. Run `make pipeline` first.")
        st.stop()
    df = pd.read_parquet(PARQUET_PATH)
    for column in ["charging_level", "placement_type", "pricing_mode"]:
        df[column] = df[column].fillna("Not specified")
    df["charging_level_label"] = df["charging_level"].map(format_label)
    df["placement_type_label"] = df["placement_type"].map(format_label)
    df["pricing_mode_label"] = df["pricing_mode"].map(format_label)
    return df


def format_label(value: object) -> str:
    if pd.isna(value):
        return "Not specified"
    text = str(value).strip()
    if not text:
        return "Not specified"
    if text.upper() == "BRCC":
        return "BRCC"
    return text[:1].upper() + text[1:]


def format_percent(value: float) -> str:
    return f"{value:.1%}"


def bar_chart(data: pd.DataFrame, x: str, y: str, color: str, height: int = 210) -> alt.Chart:
    return (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color=color)
        .encode(
            x=alt.X(f"{x}:N", title=None, sort="-y", axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{y}:Q", title=None),
            tooltip=[
                alt.Tooltip(f"{x}:N", title="Category"),
                alt.Tooltip(f"{y}:Q", title="Stations", format=","),
            ],
        )
        .properties(height=height, background="#ffffff")
        .configure_view(strokeWidth=0)
        .configure_axis(
            domain=False,
            gridColor="#edf2f7",
            labelColor="#718096",
            tickColor="#edf2f7",
            titleColor="#718096",
        )
    )


def station_scatter(data: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(data)
        .mark_circle(size=42, color="#31cdbd", opacity=0.72)
        .encode(
            x=alt.X("longitude:Q", title=None, scale=alt.Scale(zero=False), axis=None),
            y=alt.Y("latitude:Q", title=None, scale=alt.Scale(zero=False), axis=None),
            tooltip=[
                alt.Tooltip("station_id:N", title="Station"),
                alt.Tooltip("site_name:N", title="Site"),
                alt.Tooltip("charging_level_label:N", title="Charging level"),
                alt.Tooltip("placement_type_label:N", title="Placement type"),
            ],
        )
        .properties(height=390, background="#f8fbff")
        .configure_view(stroke="#e9eef5", strokeWidth=1)
    )


def build_station_map(data: pd.DataFrame) -> folium.Map:
    station_map = folium.Map(
        location=[45.52, -73.62],
        zoom_start=10,
        tiles="CartoDB positron",
        control_scale=False,
    )
    for row in data.itertuples(index=False):
        folium.CircleMarker(
            location=[row.latitude, row.longitude],
            radius=3,
            color="#1da99c",
            fill=True,
            fill_color="#31cdbd",
            fill_opacity=0.72,
            weight=1,
            tooltip=f"{row.station_id} | {row.charging_level_label}",
        ).add_to(station_map)
    return station_map


df = load_data()

with st.sidebar:
    st.markdown("## Dashboard Controls")
    st.markdown("#### Filters")
    charging_levels = sorted(df["charging_level_label"].dropna().unique())
    placement_types = sorted(df["placement_type_label"].dropna().unique())
    pricing_modes = sorted(df["pricing_mode_label"].dropna().unique())

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
    df["charging_level_label"].isin(selected_levels)
    & df["placement_type_label"].isin(selected_placements)
    & df["pricing_mode_label"].isin(selected_pricing)
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
            "charging_level_label",
            "pricing_mode",
            "pricing_mode_label",
            "placement_type",
            "placement_type_label",
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
fast_chargers = int((filtered["charging_level_label"] == "BRCC").sum())
on_street = int(filtered["is_on_street"].sum())
on_street_share = on_street / total_stations if total_stations else 0

st.markdown(
    """
    <div class="hero">
        <div class="hero-copy">
            <div class="hero-kicker"><span class="hero-icon">E</span> Montreal Mobility Analytics</div>
            <h1>EV Charging Network</h1>
            <p>Public charging infrastructure across Montreal.</p>
        </div>
        <div class="ev-scene">
            <div class="ev-road"></div>
            <div class="ev-cable"></div>
            <div class="ev-car">
                <div class="ev-port"></div>
                <div class="ev-wheel left"></div>
                <div class="ev-wheel right"></div>
            </div>
            <div class="ev-charger"></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
metric_cols[0].metric("Stations", f"{total_stations:,}")
metric_cols[1].metric("Sites", f"{total_sites:,}")
metric_cols[2].metric("Fast chargers", f"{fast_chargers:,}")
metric_cols[3].metric("On-street share", format_percent(on_street_share))

st.write("")

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    with st.container(border=True):
        st.markdown('<div class="section-title">Charging Stations Map</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="subtle">Street map of public charging station locations across Greater Montreal.</div>',
            unsafe_allow_html=True,
        )
        map_df = filtered[
            [
                "latitude",
                "longitude",
                "station_id",
                "site_name",
                "charging_level_label",
                "placement_type_label",
            ]
        ].dropna()
        st_folium(
            build_station_map(map_df),
            height=390,
            width=None,
            returned_objects=[],
        )

with right_col:
    with st.container(border=True):
        st.markdown('<div class="section-title">Network Mix</div>', unsafe_allow_html=True)
        level_counts = (
            filtered["charging_level_label"]
            .value_counts()
            .rename_axis("charging_level")
            .reset_index(name="station_count")
        )
        st.altair_chart(
            bar_chart(level_counts, "charging_level", "station_count", "#31cdbd", height=170),
            width="stretch",
        )

        placement_counts = (
            filtered["placement_type_label"]
            .value_counts()
            .rename_axis("placement_type")
            .reset_index(name="station_count")
        )
        st.altair_chart(
            bar_chart(placement_counts, "placement_type", "station_count", "#172033", height=170),
            width="stretch",
        )

pricing_counts = (
    filtered["pricing_mode_label"]
    .value_counts()
    .rename_axis("pricing_mode")
    .reset_index(name="station_count")
)

with st.container(border=True):
    st.markdown('<div class="section-title">Pricing Modes</div>', unsafe_allow_html=True)
    pricing_cols = st.columns(3)
    for index, row in enumerate(pricing_counts.itertuples(index=False)):
        with pricing_cols[index % 3]:
            st.metric(row.pricing_mode, f"{row.station_count:,}")

with st.container(border=True):
    st.markdown('<div class="section-title">Top Charging Sites</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtle">Sites with the largest number of public chargers.</div>',
        unsafe_allow_html=True,
    )
    top_sites = site_summary.sort_values(["station_count", "site_name"], ascending=[False, True]).head(10)
    st.dataframe(
        top_sites[
            [
                "site_name",
                "address",
                "charging_level_label",
                "station_count",
            ]
        ].rename(
            columns={
                "site_name": "Site",
                "address": "Address",
                "charging_level_label": "Charging level",
                "station_count": "Stations",
            }
        ),
        column_config={
            "Site": st.column_config.TextColumn(width="medium"),
            "Address": st.column_config.TextColumn(width="large"),
            "Charging level": st.column_config.TextColumn(width="small"),
            "Stations": st.column_config.NumberColumn(width="small"),
        },
        height=388,
        width="stretch",
        hide_index=True,
    )

with st.container(border=True):
    st.markdown('<div class="section-title">Station-Level Data</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtle">Searchable station-level table for detailed review.</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(
        filtered[
            [
                "station_id",
                "site_name",
                "address",
                "city",
                "charging_level_label",
                "pricing_mode_label",
                "placement_type_label",
                "latitude",
                "longitude",
            ]
        ].rename(
            columns={
                "station_id": "Station",
                "site_name": "Site",
                "address": "Address",
                "city": "City",
                "charging_level_label": "Charging level",
                "pricing_mode_label": "Pricing mode",
                "placement_type_label": "Placement type",
                "latitude": "Latitude",
                "longitude": "Longitude",
            }
        ),
        column_config={
            "Station": st.column_config.TextColumn(width="small"),
            "Site": st.column_config.TextColumn(width="large"),
            "Address": st.column_config.TextColumn(width="large"),
            "City": st.column_config.TextColumn(width="small"),
            "Charging level": st.column_config.TextColumn(width="small"),
            "Pricing mode": st.column_config.TextColumn(width="small"),
            "Placement type": st.column_config.TextColumn(width="small"),
            "Latitude": st.column_config.NumberColumn(width="small", format="%.5f"),
            "Longitude": st.column_config.NumberColumn(width="small", format="%.5f"),
        },
        height=430,
        width="stretch",
        hide_index=True,
    )
