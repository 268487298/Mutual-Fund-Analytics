import pandas as pd
import sqlite3
from pathlib import Path

# =========================
# Database Connection
# =========================

DB_PATH = "data/db/bluestock_mf.db"

conn = sqlite3.connect(DB_PATH)

print("Connected to SQLite database.")

# =========================
# File Paths
# =========================

DATA_DIR = Path("data/processed")

fund_master = pd.read_csv(DATA_DIR / "clean_fund_master.csv")
nav_history = pd.read_csv(DATA_DIR / "clean_nav_history.csv")
transactions = pd.read_csv(DATA_DIR / "clean_investor_transactions.csv")
performance = pd.read_csv(DATA_DIR / "clean_scheme_performance.csv")
portfolio = pd.read_csv(DATA_DIR / "clean_portfolio_holdings.csv")
aum = pd.read_csv(DATA_DIR / "clean_aum_by_fund_house.csv")
sip = pd.read_csv(DATA_DIR / "clean_monthly_sip_inflows.csv")
category_inflows = pd.read_csv(DATA_DIR / "clean_category_inflows.csv")
folio_count = pd.read_csv(DATA_DIR / "clean_industry_folio_count.csv")
benchmark = pd.read_csv(DATA_DIR / "clean_benchmark_indices.csv")

# =========================
# Create dim_date
# =========================

date_columns = []

for df, col in [
    (nav_history, "nav_date"),
    (transactions, "transaction_date"),
    (performance, "as_of_date"),
    (portfolio, "date"),
    (aum, "date"),
    (sip, "month"),
    (benchmark, "date")
]:
    if col in df.columns:
        date_columns.append(
            pd.to_datetime(df[col], errors="coerce")
        )

all_dates = pd.concat(date_columns).dropna().drop_duplicates()

dim_date = pd.DataFrame({
    "date": sorted(all_dates.unique())
})

dim_date["year"] = dim_date["date"].dt.year
dim_date["quarter"] = dim_date["date"].dt.quarter
dim_date["month"] = dim_date["date"].dt.month
dim_date["IS_weekday"] = dim_date["date"].dt.dayofweek < 5

# =========================
# Load Tables
# =========================

print("Loading dim_fund...")
fund_master.to_sql(
    "dim_fund",
    conn,
    if_exists="append",
    index=False
)

print("Loading dim_date...")
dim_date.to_sql(
    "dim_date",
    conn,
    if_exists="append",
    index=False
)

print("Loading fact_nav...")
nav_history.to_sql(
    "fact_nav",
    conn,
    if_exists="append",
    index=False
)

print("Loading fact_transactions...")
transactions.to_sql(
    "fact_transactions",
    conn,
    if_exists="append",
    index=False
)

print("Loading fact_performance...")
performance.to_sql(
    "fact_performance",
    conn,
    if_exists="append",
    index=False
)

print("Loading fact_portfolio...")
portfolio.to_sql(
    "fact_portfolio",
    conn,
    if_exists="append",
    index=False
)

print("Loading fact_aum...")
aum.to_sql(
    "fact_aum",
    conn,
    if_exists="append",
    index=False
)

print("Loading fact_sip_industry...")
sip.to_sql(
    "fact_sip_industry",
    conn,
    if_exists="append",
    index=False
)

print("Loading fact_category_inflows...")
category_inflows.to_sql(
    "fact_category_inflows",
    conn,
    if_exists="append",
    index=False
)

print("Loading fact_industry_folio_count...")
folio_count.to_sql(
    "fact_industry_folio_count",
    conn,
    if_exists="append",
    index=False
)

print("Loading fact_benchmark_indices...")
benchmark.to_sql(
    "fact_benchmark_indices",
    conn,
    if_exists="append",
    index=False
)

# =========================
# Verification
# =========================

tables = [
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
    "fact_benchmark_indices"
]

print("\nRow Counts")
print("-" * 40)

for table in tables:
    count = pd.read_sql(
        f"SELECT COUNT(*) AS cnt FROM {table}",
        conn
    )["cnt"][0]

    print(f"{table:<30} {count:,}")

conn.commit()
conn.close()

print("\nData loading completed successfully.")