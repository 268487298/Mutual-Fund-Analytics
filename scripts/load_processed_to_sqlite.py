"""Load cleaned processed datasets into the project's SQLite database."""

from pathlib import Path
import sqlite3
from typing import Dict, List

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "processed"
DB_DIR = ROOT_DIR / "data" / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "bluestock_mf.db"
DATE_COLUMNS: Dict[str, List[str]] = {
    "clean_fund_master.csv": ["launch_date"],
    "clean_nav_history.csv": ["date"],
    "clean_investor_transactions.csv": ["transaction_date"],
    "clean_portfolio_holdings.csv": ["portfolio_date"],
    "clean_aum_by_fund_house.csv": ["date"],
    "clean_benchmark_indices.csv": ["date"],
}

TABLES = [
    "dim_fund",
    "dim_date",
    "fact_nav",
    "fact_transactions",
    "fact_performance",
    "fact_portfolio",
    "fact_aum",
    "fact_sip_industry",
    "fact_category_inflows",
    "fact_industry_folio_count",
    "fact_benchmark_indices",
]


def load_processed_csv(filename: str) -> pd.DataFrame:
    """Load a processed CSV file and coerce date fields to datetime."""
    path = DATA_DIR / filename
    parse_dates = DATE_COLUMNS.get(filename, [])
    df = pd.read_csv(path, parse_dates=parse_dates)
    for date_col in parse_dates:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    return df


def build_dim_date() -> pd.DataFrame:
    """Build a dimension table of unique dates across processed datasets."""
    date_series = []
    sources = {
        "clean_nav_history.csv": "date",
        "clean_investor_transactions.csv": "transaction_date",
        "clean_scheme_performance.csv": "as_of_date",
        "clean_portfolio_holdings.csv": "portfolio_date",
        "clean_aum_by_fund_house.csv": "date",
        "clean_monthly_sip_inflows.csv": "month",
        "clean_benchmark_indices.csv": "date",
    }
    for filename, date_column in sources.items():
        path = DATA_DIR / filename
        df = pd.read_csv(path)
        if date_column in df.columns:
            date_series.append(pd.to_datetime(df[date_column], errors="coerce"))

    if not date_series:
        raise ValueError("No date columns found when building dim_date.")
    all_dates = pd.concat(date_series).dropna().drop_duplicates()
    dim_date = pd.DataFrame({"date": sorted(all_dates.unique())})
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["quarter"] = dim_date["date"].dt.quarter
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["is_weekday"] = dim_date["date"].dt.dayofweek < 5
    return dim_date


def write_table(conn: sqlite3.Connection, table_name: str, df: pd.DataFrame) -> None:
    """Write a DataFrame to SQLite, replacing existing contents."""
    df.to_sql(table_name, conn, if_exists="replace", index=False)


def print_row_counts(conn: sqlite3.Connection) -> None:
    """Print row counts for all loaded tables."""
    for table in TABLES:
        count = pd.read_sql(f"SELECT COUNT(*) AS cnt FROM {table}", conn)["cnt"][0]
        print(f"{table:<30} {count:,}")


def main() -> int:
    """Load all cleaned processed datasets into the SQLite database."""
    with sqlite3.connect(DB_PATH) as conn:
        write_table(conn, "dim_fund", load_processed_csv("clean_fund_master.csv"))
        write_table(conn, "dim_date", build_dim_date())
        write_table(conn, "fact_nav", load_processed_csv("clean_nav_history.csv"))
        write_table(conn, "fact_transactions", load_processed_csv("clean_investor_transactions.csv"))
        write_table(conn, "fact_performance", pd.read_csv(DATA_DIR / "clean_scheme_performance.csv"))
        write_table(conn, "fact_portfolio", load_processed_csv("clean_portfolio_holdings.csv"))
        write_table(conn, "fact_aum", load_processed_csv("clean_aum_by_fund_house.csv"))
        write_table(conn, "fact_sip_industry", pd.read_csv(DATA_DIR / "clean_monthly_sip_inflows.csv"))
        write_table(conn, "fact_category_inflows", pd.read_csv(DATA_DIR / "clean_category_inflows.csv"))
        write_table(conn, "fact_industry_folio_count", pd.read_csv(DATA_DIR / "clean_industry_folio_count.csv"))
        write_table(conn, "fact_benchmark_indices", load_processed_csv("clean_benchmark_indices.csv"))
        conn.commit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
