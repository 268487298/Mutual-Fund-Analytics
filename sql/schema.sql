CREATE TABLE dim_fund (
    amfi_code TEXT PRIMARY KEY,
    fund_house TEXT,
    scheme_name TEXT,
    category TEXT,
    sub_category TEXT,
    expense_ratio REAL
);

CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    IS_weekday BOOLEAN
);

CREATE TABLE fact_nav (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT,
    nav_date DATE,
    nav REAL,
    daily_return REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT,
    transaction_date DATE,
    transaction_type TEXT,
    units REAL,
    amount REAL,
    nav_at_transaction REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_performance (
    amfi_code TEXT,
    as_of_date DATE,
    annual_return REAL,
    sharpe_ratio REAL,
    volatility REAL,
    expense_ratio_pct REAL,
    risk_score REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);


CREATE TABLE fact_portfolio (
    portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT,
    stock_symbol TEXT,
    weight_pct REAL,
    sector TEXT,
    date DATE,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_aum (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house TEXT,
    date DATE,
    aum_crore REAL,
    num_schemes INTEGER
);

CREATE TABLE fact_sip_industry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE,
    sip_inflow_crore REAL,
    sip_accounts_crore REAL
);

CREATE TABLE fact_category_inflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month INTEGER,
    category TEXT,
    net_inflow_crore REAL
);

CREATE TABLE fact_industry_folio_count (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month INTEGER,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

CREATE TABLE fact_benchmark_indices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    index_name TEXT,
    close_value REAL
);

