from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st


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

    .mock-panel {
        position: absolute;
        right: 42px;
        bottom: -8px;
        z-index: 3;
        width: 330px;
        padding: 18px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.93);
        box-shadow: 0 18px 40px rgba(23, 32, 51, 0.18);
    }

    .mock-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 12px;
    }

    .mock-card {
        height: 50px;
        border-radius: 8px;
        background: #f7fbfd;
        border: 1px solid #e5eef6;
    }

    .mock-chart {
        height: 86px;
        border-radius: 8px;
        background:
            linear-gradient(180deg, rgba(29, 169, 156, 0.22), rgba(29, 169, 156, 0.04)),
            repeating-linear-gradient(0deg, transparent 0, transparent 19px, #d9e7ef 20px);
        border: 1px solid #dce9f1;
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

    @media (max-width: 1100px) {
        .mock-panel {
            display: none;
        }
        .hero::after {
            display: none;
        }
        .hero h1 {
            font-size: 34px;
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
        df[column] = df[column].fillna("Unknown")
    return df


def format_percent(value: float) -> str:
    return f"{value:.1%}"


def bar_chart(data: pd.DataFrame, x: str, y: str, color: str) -> alt.Chart:
    return (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color=color)
        .encode(
            x=alt.X(f"{x}:N", title=None, sort="-y", axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{y}:Q", title=None),
            tooltip=[x, y],
        )
        .properties(height=220)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#edf2f7", labelColor="#718096", tickColor="#edf2f7")
    )


df = load_data()

with st.sidebar:
    st.markdown("## Dashboard Controls")
    st.markdown("#### Filters")
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

st.markdown(
    """
    <div class="hero">
        <div class="hero-copy">
            <div class="hero-kicker"><span class="hero-icon">E</span> Montreal Mobility Analytics</div>
            <h1>EV Charging Network</h1>
            <p>Public charging infrastructure across Montreal.</p>
        </div>
        <div class="mock-panel">
            <div class="mock-row">
                <div class="mock-card"></div>
                <div class="mock-card"></div>
            </div>
            <div class="mock-chart"></div>
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

left_col, right_col = st.columns([1.2, 0.8], gap="large")

with left_col:
    with st.container(border=True):
        st.markdown('<div class="section-title">Charging Stations Map</div>', unsafe_allow_html=True)
        map_df = filtered[["latitude", "longitude", "station_id", "site_name", "charging_level"]].dropna()
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[longitude, latitude]",
            get_fill_color="[49, 205, 189, 180]",
            get_radius=70,
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=45.52, longitude=-73.62, zoom=9.6, pitch=0)
        st.pydeck_chart(
            pdk.Deck(
                map_style="light",
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{station_id}\\n{site_name}\\n{charging_level}"},
            ),
            height=430,
        )

with right_col:
    with st.container(border=True):
        st.markdown('<div class="section-title">Network Mix</div>', unsafe_allow_html=True)
        level_counts = (
            filtered["charging_level"]
            .value_counts()
            .rename_axis("charging_level")
            .reset_index(name="station_count")
        )
        st.altair_chart(
            bar_chart(level_counts, "charging_level", "station_count", "#31cdbd"),
            width="stretch",
        )

        placement_counts = (
            filtered["placement_type"]
            .value_counts()
            .rename_axis("placement_type")
            .reset_index(name="station_count")
        )
        st.altair_chart(
            bar_chart(placement_counts, "placement_type", "station_count", "#172033"),
            width="stretch",
        )

top_left, top_right = st.columns([1.35, 0.65], gap="large")

with top_left:
    with st.container(border=True):
        st.markdown('<div class="section-title">Top Charging Sites</div>', unsafe_allow_html=True)
        top_sites = site_summary.sort_values(["station_count", "site_name"], ascending=[False, True]).head(15)
        st.dataframe(
            top_sites[["site_name", "address", "charging_level", "placement_type", "station_count"]],
            width="stretch",
            hide_index=True,
        )

with top_right:
    with st.container(border=True):
        st.markdown('<div class="section-title">Pricing Modes</div>', unsafe_allow_html=True)
        pricing_counts = (
            filtered["pricing_mode"]
            .value_counts()
            .rename_axis("pricing_mode")
            .reset_index(name="station_count")
        )
        st.dataframe(pricing_counts, width="stretch", hide_index=True)

with st.container(border=True):
    st.markdown('<div class="section-title">Station-Level Data</div>', unsafe_allow_html=True)
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
