"""Export the mart tables from the DuckDB file to CSV, for Power BI to read.

Run from the project folder after `dbt build`:
    python scripts/export_marts.py
"""
from pathlib import Path

import duckdb

TABLES = [
    "fct_orders",
    "dim_customers",
    "fct_lead_funnel",
    "mart_funnel_by_origin",
    "mart_cohort_retention",
]

out_dir = Path("exports")
out_dir.mkdir(exist_ok=True)

con = duckdb.connect("olist.duckdb", read_only=True)
for table in TABLES:
    target = (out_dir / f"{table}.csv").as_posix()
    con.execute(f"copy (select * from {table}) to '{target}' (header, delimiter ',')")
    rows = con.execute(f"select count(*) from {table}").fetchone()[0]
    print(f"{table}: {rows:,} rows -> {target}")
con.close()