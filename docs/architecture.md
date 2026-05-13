# Architecture

The pipeline follows a simple lakehouse-style layout that is easy to explain in interviews.

## Raw zone

The raw zone stores the original CSV and GeoJSON from Montreal open data. Files are kept unchanged so the pipeline is reproducible and auditable.

## Processed zone

The processed zone stores a cleaned Parquet table. Transformations include:

- French source columns renamed to snake_case English names
- text cleanup for addresses and categorical fields
- station and site identifiers extracted
- coordinate validation between CSV and GeoJSON
- boolean flag for on-street chargers

## Analytics zone

DuckDB loads the Parquet table and exposes SQL-friendly objects:

- `charging_stations`: station-level table
- `site_summary`: grouped site-level view

This local setup maps cleanly to a cloud version using S3, Glue, and Athena.
