# Data Dictionary

## Overview
This document describes all tables, columns, data types, and sources in the Bluestock Mutual Analytics database (`bluestock_mf.db`).

---

## Dimension Tables

### dim_fund
**Description:** Master data for mutual fund schemes  
**Source:** `data/raw/01_fund_master.csv`  
**Row Count:** Dynamic (loaded from source CSV)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| amfi_code | TEXT | AMFI scheme code (unique identifier) | Primary Key |
| fund_house | TEXT | Fund house/AMC name (e.g., SBI Mutual Fund) | |
| scheme_name | TEXT | Full scheme name | |
| category | TEXT | Scheme category (Equity, Debt, Hybrid, etc.) | |
| sub_category | TEXT | Scheme subcategory (Large Cap, Small Cap, etc.) | |
| expense_ratio | REAL | Annual expense ratio (%) | From source data |
| plan | TEXT | Plan type (Regular, Direct) | |
| launch_date | DATE | Fund launch date | Not in DB schema but in source |
| benchmark | TEXT | Benchmark index name | Not in DB schema but in source |
| exit_load_pct | REAL | Exit load percentage | Not in DB schema but in source |
| min_sip_amount | INTEGER | Minimum SIP amount (₹) | Not in DB schema but in source |
| min_lumpsum_amount | INTEGER | Minimum lumpsum investment (₹) | Not in DB schema but in source |
| fund_manager | TEXT | Fund manager name | Not in DB schema but in source |
| risk_category | TEXT | Risk category (Low, Moderate, High, Very High) | Not in DB schema but in source |
| sebi_category_code | TEXT | SEBI category code | Not in DB schema but in source |

---

### dim_date
**Description:** Date dimension for time-based analysis  
**Source:** Generated during ETL process (not loaded from CSV)  
**Purpose:** Enables efficient date-based filtering and aggregations

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| date_id | INTEGER | Unique date identifier | Primary Key (Auto-increment) |
| date | DATE | Calendar date | Unique constraint |
| year | INTEGER | Year (YYYY) | |
| quarter | INTEGER | Quarter (1-4) | |
| month | INTEGER | Month (1-12) | |
| IS_weekday | BOOLEAN | True if weekday, False if weekend | |

---

## Fact Tables

### fact_nav
**Description:** Daily Net Asset Value (NAV) history for funds  
**Source:** `data/raw/02_nav_history.csv`  
**Row Count:** Dynamic (daily records)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| id | INTEGER | Unique record identifier | Primary Key (Auto-increment) |
| amfi_code | TEXT | AMFI scheme code | Foreign Key → dim_fund(amfi_code) |
| nav_date | DATE | Date of NAV value | |
| nav | REAL | Net Asset Value per unit (₹) | |
| daily_return | REAL | Daily return percentage | Computed field (not in source CSV) |

---

### fact_transactions
**Description:** Investor transactions (SIP, lumpsum, redemptions)  
**Source:** `data/raw/08_investor_transactions.csv`  
**Row Count:** Dynamic (transaction records)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| transaction_id | INTEGER | Unique transaction identifier | Primary Key (Auto-increment) |
| amfi_code | TEXT | AMFI scheme code | Foreign Key → dim_fund(amfi_code) |
| transaction_date | DATE | Date of transaction | |
| transaction_type | TEXT | Type: SIP, Lumpsum, Redemption | |
| units | REAL | Number of units transacted | Computed from amount/NAV; not in source |
| amount | REAL | Transaction amount in INR | |
| nav_at_transaction | REAL | NAV at transaction date | Computed field; not in source |
| investor_id | TEXT | Unique investor identifier | In source CSV but not in DB schema |
| state | TEXT | Investor state | In source CSV but not in DB schema |
| city | TEXT | Investor city | In source CSV but not in DB schema |
| city_tier | TEXT | City tier classification (T30, B30, etc.) | In source CSV but not in DB schema |
| age_group | TEXT | Investor age group | In source CSV but not in DB schema |
| gender | TEXT | Investor gender (M/F) | In source CSV but not in DB schema |
| annual_income_lakh | REAL | Annual income in lakhs (₹) | In source CSV but not in DB schema |
| payment_mode | TEXT | Payment mode (UPI, Cheque, Mandate, etc.) | In source CSV but not in DB schema |
| kyc_status | TEXT | KYC verification status (Verified, Pending) | In source CSV but not in DB schema |

---

### fact_performance
**Description:** Scheme performance metrics and risk indicators  
**Source:** `data/raw/07_scheme_performance.csv`  
**Row Count:** Dynamic (one record per scheme per date)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| amfi_code | TEXT | AMFI scheme code | Foreign Key → dim_fund(amfi_code); Composite PK with as_of_date |
| as_of_date | DATE | Date as of which metrics are calculated | Composite PK with amfi_code |
| annual_return | REAL | 1-year return (%) | From source field: return_1yr_pct |
| sharpe_ratio | REAL | Sharpe ratio (risk-adjusted return) | |
| volatility | REAL | Annual standard deviation (%) | From source field: std_dev_ann_pct |
| expense_ratio_pct | REAL | Annual expense ratio (%) | From source field: expense_ratio_pct |
| risk_score | REAL | Custom risk score | |
| return_3yr_pct | REAL | 3-year return (%) | In source but not in DB schema |
| return_5yr_pct | REAL | 5-year return (%) | In source but not in DB schema |
| benchmark_3yr_pct | REAL | Benchmark 3-year return (%) | In source but not in DB schema |
| alpha | REAL | Jensen's alpha | In source but not in DB schema |
| beta | REAL | Beta coefficient | In source but not in DB schema |
| sortino_ratio | REAL | Sortino ratio | In source but not in DB schema |
| max_drawdown_pct | REAL | Maximum drawdown (%) | In source but not in DB schema |
| aum_crore | REAL | Assets Under Management (₹ crore) | In source but not in DB schema |
| morningstar_rating | INTEGER | Morningstar rating (1-5 stars) | In source but not in DB schema |
| risk_grade | TEXT | Risk grade (Low, Moderate, High, Very High) | In source but not in DB schema |

---

### fact_portfolio
**Description:** Fund portfolio holdings - individual stocks/securities  
**Source:** `data/raw/09_portfolio_holdings.csv`  
**Row Count:** Dynamic (one record per holding per fund per date)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| portfolio_id | INTEGER | Unique portfolio holding identifier | Primary Key (Auto-increment) |
| amfi_code | TEXT | AMFI scheme code | Foreign Key → dim_fund(amfi_code) |
| stock_symbol | TEXT | Stock ticker/symbol | |
| weight_pct | REAL | Weight in portfolio (%) | |
| sector | TEXT | Sector classification | |
| date | DATE | Portfolio snapshot date | |
| stock_name | TEXT | Full stock name | In source but not in DB schema |
| market_value_cr | REAL | Market value in ₹ crore | In source but not in DB schema |
| current_price_inr | REAL | Current stock price in INR | In source but not in DB schema |

---

### fact_aum
**Description:** Assets Under Management by fund house over time  
**Source:** `data/raw/03_aum_by_fund_house.csv`  
**Row Count:** Dynamic (monthly records per fund house)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| id | INTEGER | Unique record identifier | Primary Key (Auto-increment) |
| fund_house | TEXT | Fund house/AMC name | |
| date | DATE | Month-end date | |
| aum_crore | REAL | Total AUM in ₹ crore | |
| num_schemes | INTEGER | Number of schemes offered | |
| aum_lakh_crore | REAL | Total AUM in ₹ lakh crore | In source but not in DB schema |

---

### fact_sip_industry
**Description:** Industry-wide SIP (Systematic Investment Plan) metrics  
**Source:** `data/raw/04_monthly_sip_inflows.csv`  
**Row Count:** Dynamic (monthly records)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| id | INTEGER | Unique record identifier | Primary Key (Auto-increment) |
| month | DATE | Month for which data is reported | |
| sip_inflow_crore | REAL | Monthly SIP inflows in ₹ crore | |
| sip_accounts_crore | REAL | Active SIP accounts (in crore) | From source: active_sip_accounts_crore |
| new_sip_accounts_lakh | REAL | New SIP accounts opened (in lakh) | In source but not in DB schema |
| sip_aum_lakh_crore | REAL | SIP AUM in ₹ lakh crore | In source but not in DB schema |
| yoy_growth_pct | REAL | Year-over-year growth (%) | In source but not in DB schema |

---

### fact_category_inflows
**Description:** Net inflows to fund categories  
**Source:** `data/raw/05_category_inflows.csv`  
**Row Count:** Dynamic (monthly records per category)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| id | INTEGER | Unique record identifier | Primary Key (Auto-increment) |
| month | INTEGER | Month as integer (1-12) | |
| category | TEXT | Fund category (Large Cap, Small Cap, Debt, etc.) | |
| net_inflow_crore | REAL | Net inflows in ₹ crore | |

---

### fact_industry_folio_count
**Description:** Total folios (investor accounts) by category across the industry  
**Source:** `data/raw/06_industry_folio_count.csv`  
**Row Count:** Dynamic (monthly records)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| id | INTEGER | Unique record identifier | Primary Key (Auto-increment) |
| month | INTEGER | Month as integer (1-12) | |
| total_folios_crore | REAL | Total folios in crore | |
| equity_folios_crore | REAL | Equity category folios in crore | |
| debt_folios_crore | REAL | Debt category folios in crore | |
| hybrid_folios_crore | REAL | Hybrid category folios in crore | |
| others_folios_crore | REAL | Other categories folios in crore | |

---

### fact_benchmark_indices
**Description:** Benchmark index values for performance comparison  
**Source:** `data/raw/10_benchmark_indices.csv`  
**Row Count:** Dynamic (daily records per index)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| id | INTEGER | Unique record identifier | Primary Key (Auto-increment) |
| date | DATE | Index date | |
| index_name | TEXT | Index name (NIFTY50, NIFTY100, SENSEX, etc.) | |
| close_value | REAL | Index closing value | |

---

## Data Type Mapping

| SQLite Type | Description |
|------------|-------------|
| INTEGER | Whole numbers (IDs, counts) |
| REAL | Floating-point numbers (prices, percentages, ratios) |
| TEXT | Text strings (names, codes, categories) |
| DATE | Date values (YYYY-MM-DD format) |
| BOOLEAN | Boolean values (0=False, 1=True) |

---

## Entity Relationships

```
dim_fund (amfi_code)
├── ├─ fact_nav (amfi_code)
├── ├─ fact_transactions (amfi_code)
├── ├─ fact_performance (amfi_code)
└── └─ fact_portfolio (amfi_code)

fact_performance (amfi_code)
└── dim_fund (amfi_code)

dim_date (date)
├── fact_nav (nav_date)
├── fact_transactions (transaction_date)
└── fact_aum (date)
```

---

## Data Loading Pipeline

1. **Source CSVs** → `data/raw/*.csv`
2. **Validation** → Performed in `main.py`
3. **Load Process** → Pandas reads CSVs, loads to SQLite via `to_sql()`
4. **Destination** → `data/db/bluestock_mf.db`

**Entry Point:** `main.py` orchestrates the entire ETL process

---

## Notes & Considerations

- **Raw CSV Files:** Stored in `data/raw/` with numbered prefixes (01-10) matching load order
- **Processed CSVs:** Cleaned outputs in `data/processed/` for quick access without DB query
- **Computed Fields:** Some columns (e.g., daily_return, units) may be computed during ETL
- **Missing Data:** Check actual CSV files for NULL/empty value handling in cleaned data
- **Date Format:** All dates stored as DATE or text in YYYY-MM-DD format
- **Currency:** All monetary values in Indian Rupees (₹) unless otherwise noted
- **Scale:** Large values (AUM, inflows) often expressed in crore (10 million)

---

## Related Documentation

- **Schema Definition:** See [sql/schema.sql](sql/schema.sql)
- **ETL Process:** See [main.py](main.py)
- **Analysis Notebooks:** See `notebooks/` directory
- **Queries:** See [sql/queries.sql](sql/queries.sql)
