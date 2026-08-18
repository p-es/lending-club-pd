from pathlib import Path
import duckdb

DB_PATH = Path("data/processed/lending.duckdb")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))

def run_sql_file(con, path):
    con.execute(Path(path).read_text())
    