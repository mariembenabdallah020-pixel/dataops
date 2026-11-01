
import duckdb
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: python load_raw.py <csv_file>")
    sys.exit(1)

csv_file = Path(sys.argv[1])

if not csv_file.exists():
    print(f"File not found: {csv_file}")
    sys.exit(1)

con = duckdb.connect("warehouse.duckdb")

con.execute("CREATE SCHEMA IF NOT EXISTS raw")

con.execute("""
    CREATE OR REPLACE TABLE raw.orders AS
    SELECT
        *,
        row_number() OVER () AS _row_number,
        ? AS _source_file,
        current_timestamp AS _loaded_at
    FROM read_csv(?, all_varchar = true)
""", [str(csv_file), str(csv_file)])

count = con.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0]

print(f"Loaded {count} rows into raw.orders")

con.close()
