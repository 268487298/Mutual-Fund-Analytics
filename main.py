"""Load raw mutual fund CSV files into the local SQLite database."""

import os
import sqlite3
import sys
from typing import Dict

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DB_PATH = os.path.join(BASE_DIR, "bluestock_mf.db")
FILES = {
    "dim_fund": "01_fund_master.csv",
    "fact_nav": "02_nav_history.csv",
    "fact_transactions": "08_investor_transactions.csv",
    "fact_performance": "07_scheme_performance.csv",
}


def validate_raw_files(raw_dir: str, files: Dict[str, str]) -> None:
    """Ensure required raw CSV files are present before loading."""
    missing_files = []
    for dataset_name, csv_file in files.items():
        csv_path = os.path.join(raw_dir, csv_file)
        if not os.path.exists(csv_path):
            missing_files.append((dataset_name, csv_path))

    if missing_files:
        for dataset_name, csv_path in missing_files:
            print(f"Missing CSV file for {dataset_name}: {csv_path}")
        raise FileNotFoundError("Required raw CSV files are missing.")


def load_csv_files(raw_dir: str) -> Dict[str, pd.DataFrame]:
    """Read raw CSV files into pandas DataFrames."""
    return {
        "dim_fund": pd.read_csv(os.path.join(raw_dir, FILES["dim_fund"])),
        "fact_nav": pd.read_csv(os.path.join(raw_dir, FILES["fact_nav"])),
        "fact_transactions": pd.read_csv(os.path.join(raw_dir, FILES["fact_transactions"])),
        "fact_performance": pd.read_csv(os.path.join(raw_dir, FILES["fact_performance"])),
    }


def print_table_info(cursor: sqlite3.Cursor, table_name: str) -> None:
    """Print row counts and schema info for a table."""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    print(f"{table_name} rows: {cursor.fetchone()[0]}")
    print(f"\n=== {table_name} columns ===")
    cursor.execute(f"PRAGMA table_info({table_name})")
    for col in cursor.fetchall():
        print(col)


def write_tables_to_db(db_path: str, tables: Dict[str, pd.DataFrame]) -> None:
    """Write DataFrames to the SQLite database."""
    with sqlite3.connect(db_path) as conn:
        for table_name, data_frame in tables.items():
            data_frame.to_sql(table_name, conn, if_exists="replace", index=False)

        cursor = conn.cursor()
        print_table_info(cursor, "dim_fund")
        print_table_info(cursor, "fact_transactions")
        conn.commit()


def main() -> int:
    """Run the raw CSV ingestion pipeline."""
    try:
        validate_raw_files(RAW_DIR, FILES)
        data_frames = load_csv_files(RAW_DIR)
        print("Raw CSV files validated and loaded.")
        write_tables_to_db(DB_PATH, data_frames)
        print("All datasets loaded into bluestock_mf.db")
        return 0
    except Exception as exc:
        print("Failed to load raw CSV files:", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
