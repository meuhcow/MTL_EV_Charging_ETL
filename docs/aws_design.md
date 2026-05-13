# AWS Deployment Design

This project can be deployed on AWS without changing the core data model.

## Services

- S3 for raw, processed, and analytics zones
- AWS Glue crawler for schema discovery
- Athena for SQL queries over Parquet
- MWAA or self-managed Airflow for orchestration
- CloudWatch for pipeline logs and alerts

## S3 layout

```text
s3://portfolio-montreal-ev/raw/bornes_recharge/date=YYYY-MM-DD/
s3://portfolio-montreal-ev/processed/charging_stations/date=YYYY-MM-DD/
s3://portfolio-montreal-ev/analytics/site_summary/
```

## Orchestration

An Airflow DAG can run monthly:

1. Download CSV and GeoJSON.
2. Write raw files to S3.
3. Transform data with Pandas or PySpark.
4. Write partitioned Parquet.
5. Run quality checks.
6. Refresh Glue catalog tables.
7. Execute Athena validation queries.
