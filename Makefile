.PHONY: pipeline analytics dashboard clean

PYTHON ?= .venv/bin/python

pipeline:
	$(PYTHON) -m src.run_pipeline

analytics:
	$(PYTHON) -m src.run_analytics

dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py

clean:
	rm -f data/raw/bornes_recharge_publiques.csv
	rm -f data/raw/bornes_recharge_publiques.geojson
	rm -f data/raw/source_metadata.json
	rm -f data/processed/charging_stations.parquet
	rm -f data/analytics/ev_charging.duckdb
	rm -f reports/data_quality_report.json
	rm -f reports/analytics_summary.csv
