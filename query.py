
import duckdb
import sys

if len(sys.argv) != 2:
    print('Usage: python query.py "SQL query"')
    sys.exit(1)

con = duckdb.connect("warehouse.duckdb", read_only=True)

result = con.execute(sys.argv[1])

print(result.df().to_string(index=False))

con.close()
