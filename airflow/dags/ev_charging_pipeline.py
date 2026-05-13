"""
Optional Airflow DAG for the Montreal EV charging pipeline.

Copy this file into an Airflow environment after the local pipeline is working.
"""

from __future__ import annotations

from datetime import datetime

try:
    from airflow.decorators import dag, task
except ImportError:
    dag = None
    task = None


if dag and task:

    @dag(
        dag_id="montreal_ev_charging_pipeline",
        start_date=datetime(2026, 1, 1),
        schedule="@monthly",
        catchup=False,
        tags=["portfolio", "etl", "montreal", "ev"],
    )
    def montreal_ev_charging_pipeline():
        @task
        def run_pipeline():
            from src.run_pipeline import main

            main()

        run_pipeline()

    montreal_ev_charging_pipeline()
