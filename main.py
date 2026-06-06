import os
import sqlite3
import sys
import pandas as pd

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DB_PATH = os.path.join(BASE_DIR, "bluestock_mf.db")

FILES = {
    "dim_fund": "01_fund_master.csv",
    "fact_nav": "02_nav_history.csv",
    "fact_transactions": "08_investor_transactions.csv",
    "fact_performance": "07_scheme_performance.csv",
}

# =========================
# CHECK FILES EXIST
# =========================
for dataset_name, csv_file in FILES.items():
    csv_path = os.path.join(RAW_DIR, csv_file)

    if not os.path.exists(csv_path):
        print(f"❌ Missing CSV file for {dataset_name}: {csv_path}")
        sys.exit(1)

# =========================
# LOAD CSV FILES
# =========================
try:
    df_fund = pd.read_csv(os.path.join(RAW_DIR, FILES["dim_fund"]))
    df_nav = pd.read_csv(os.path.join(RAW_DIR, FILES["fact_nav"]))
    df_txn = pd.read_csv(os.path.join(RAW_DIR, FILES["fact_transactions"]))
    df_perf = pd.read_csv(os.path.join(RAW_DIR, FILES["fact_performance"]))

    print("✅ CSV files loaded successfully")

except Exception as exc:
    print("❌ Failed to read CSV files:", exc)
    sys.exit(1)

# =========================
# LOAD INTO SQLITE
# =========================
conn = None

try:
    conn = sqlite3.connect(DB_PATH)

    # Load data into tables
    df_fund.to_sql("dim_fund", conn, if_exists="replace", index=False)
    df_nav.to_sql("fact_nav", conn, if_exists="replace", index=False)
    df_txn.to_sql("fact_transactions", conn, if_exists="replace", index=False)
    df_perf.to_sql("fact_performance", conn, if_exists="replace", index=False)

    cursor = conn.cursor()

    # Row counts
    cursor.execute("SELECT COUNT(*) FROM dim_fund")
    print("dim_fund rows:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM fact_nav")
    print("fact_nav rows:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM fact_transactions")
    print("fact_transactions rows:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM fact_performance")
    print("fact_performance rows:", cursor.fetchone()[0])

    # Show columns from dim_fund
    print("\n=== dim_fund columns ===")
    cursor.execute("PRAGMA table_info(dim_fund)")
    for col in cursor.fetchall():
        print(col)

    # Show columns from fact_transactions
    print("\n=== fact_transactions columns ===")
    cursor.execute("PRAGMA table_info(fact_transactions)")
    for col in cursor.fetchall():
        print(col)

    conn.commit()

    print("\n✅ All datasets loaded into bluestock_mf.db")

except Exception as exc:
    print("❌ Database error:", exc)

finally:
    if conn:
        conn.close()
        print("🔒 Database connection closed")
