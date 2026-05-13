from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ANALYTICS_DIR = DATA_DIR / "analytics"
REPORTS_DIR = BASE_DIR / "reports"

CSV_URL = (
    "https://donnees.montreal.ca/dataset/c999d1a9-8333-4871-9226-7d3a53f490a6/"
    "resource/98ef3ed6-56ca-4d5e-a213-fd72066b18b5/download/"
    "bornes-recharge-publiques.csv"
)

GEOJSON_URL = (
    "https://donnees.montreal.ca/dataset/c999d1a9-8333-4871-9226-7d3a53f490a6/"
    "resource/b502cee9-ff87-44fa-9a8e-722285202b0d/download/"
    "bornes-recharge-publiques.geojson"
)

RAW_CSV_PATH = RAW_DIR / "bornes_recharge_publiques.csv"
RAW_GEOJSON_PATH = RAW_DIR / "bornes_recharge_publiques.geojson"
SOURCE_METADATA_PATH = RAW_DIR / "source_metadata.json"
PROCESSED_PARQUET_PATH = PROCESSED_DIR / "charging_stations.parquet"
DUCKDB_PATH = ANALYTICS_DIR / "ev_charging.duckdb"
QUALITY_REPORT_PATH = REPORTS_DIR / "data_quality_report.json"
ANALYTICS_SUMMARY_PATH = REPORTS_DIR / "analytics_summary.csv"
