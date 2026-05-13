# Montreal EV Charging Data Pipeline

A compact data engineering portfolio project that ingests Montreal public electric vehicle charging station data, validates it, stores analytics-ready Parquet files, and loads curated tables into DuckDB for SQL analysis.

## Why this project

This project demonstrates practical ETL work with open civic data:

- Python data pipeline code
- CSV and GeoJSON ingestion
- JSON parsing
- Data quality checks
- Pandas and PyArrow transformations
- Parquet data lake output
- SQL analytics with DuckDB
- Optional Airflow orchestration stub
- Cloud-ready raw/processed/analytics zone design

Dataset: [Bornes de recharge publiques pour voitures electriques](https://donnees.montreal.ca/dataset/bornes-recharge-publiques), Ville de Montreal open data.

## Architecture

```text
Montreal Open Data CSV + GeoJSON
        |
        v
data/raw/
        |
        v
Python ETL + quality checks
        |
        v
data/processed/charging_stations.parquet
        |
        v
DuckDB analytics database
        |
        v
SQL reports and portfolio insights
```

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make pipeline
make analytics
```

If you do not want to use `make`, run:

```bash
python -m src.run_pipeline
duckdb data/analytics/ev_charging.duckdb < sql/analytics_queries.sql
```

## Outputs

After the pipeline runs:

- `data/raw/`: downloaded CSV, GeoJSON, and source metadata
- `data/processed/charging_stations.parquet`: cleaned station-level table
- `data/analytics/ev_charging.duckdb`: SQL analytics database
- `reports/data_quality_report.json`: validation results
- `reports/analytics_summary.csv`: portfolio-friendly summary metrics

## Example questions

- How many charging stations are available by charging level?
- How many chargers are on-street versus off-street?
- Which sites have the highest charger counts?
- Are there duplicated station IDs or invalid coordinates?
- Which pricing modes are most common?

## Project Structure

```text
.
├── airflow/dags/ev_charging_pipeline.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── analytics/
├── docs/
│   ├── architecture.md
│   └── aws_design.md
├── notebooks/01_exploration.ipynb
├── reports/
├── sql/
│   ├── create_tables.sql
│   └── analytics_queries.sql
└── src/
    ├── config.py
    ├── ingest.py
    ├── quality.py
    ├── transform.py
    ├── load.py
    └── run_pipeline.py
```

## Next portfolio upgrades

- Add the related utilization dataset and model monthly charger usage.
- Add dbt models on top of DuckDB or PostgreSQL.
- Deploy raw and processed zones to S3.
- Run the pipeline with Airflow on a schedule.
- Add a Streamlit map dashboard.
