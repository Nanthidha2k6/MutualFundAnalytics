-- ========================================================
--   Mutual Fund Analytics - Day 2: SQLite Star Schema DDL
--   File   : sql/schema.sql
--   Author : Student Project
--   Purpose: Define the tables for the star schema
-- ========================================================

-- Enable Foreign Key Support in SQLite (Note: Needs to be run per connection too)
PRAGMA foreign_keys = ON;

-- --------------------------------------------------------
-- 1. Dimension Tables
-- --------------------------------------------------------

-- dim_fund: Scheme details and metadata
CREATE TABLE IF NOT EXISTS dim_fund (
    fund_key INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT UNIQUE NOT NULL,
    scheme_name TEXT NOT NULL,
    fund_house TEXT,
    category TEXT,
    subcategory TEXT,
    risk_grade TEXT
);

-- dim_date: Calendar date dimensions for time-series analysis
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY, -- Format: YYYYMMDD
    full_date DATE UNIQUE NOT NULL, -- Format: YYYY-MM-DD
    day INTEGER NOT NULL, -- 1-31
    month INTEGER NOT NULL, -- 1-12
    month_name TEXT NOT NULL, -- January, February, ...
    quarter INTEGER NOT NULL, -- 1-4
    year INTEGER NOT NULL, -- e.g., 2026
    week_of_year INTEGER NOT NULL -- 1-53
);

-- --------------------------------------------------------
-- 2. Fact Tables
-- --------------------------------------------------------

-- fact_nav: Daily NAV records
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_key INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    nav REAL NOT NULL,
    FOREIGN KEY (fund_key) REFERENCES dim_fund(fund_key) ON DELETE CASCADE,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key) ON DELETE CASCADE,
    UNIQUE(fund_key, date_key)
);

-- fact_transactions: Investor transactions (SIP, Lumpsum, Redemption)
-- Note: This table is created as part of the schema but remains empty due to missing raw transaction data.
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_key INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('SIP', 'Lumpsum', 'Redemption')),
    amount REAL NOT NULL CHECK(amount > 0),
    kyc_status TEXT CHECK(kyc_status IN ('Yes', 'No', 'Pending')),
    investor_state TEXT,
    FOREIGN KEY (fund_key) REFERENCES dim_fund(fund_key) ON DELETE CASCADE,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key) ON DELETE CASCADE
);

-- fact_performance: Historical and current performance indicators
-- Note: This table is created as part of the schema but remains empty due to missing raw performance data.
CREATE TABLE IF NOT EXISTS fact_performance (
    performance_key INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_key INTEGER NOT NULL,
    date_key INTEGER,
    return_1m REAL,
    return_3m REAL,
    return_6m REAL,
    return_1y REAL,
    return_3y REAL,
    return_5y REAL,
    expense_ratio REAL CHECK(expense_ratio >= 0.1 AND expense_ratio <= 2.5),
    FOREIGN KEY (fund_key) REFERENCES dim_fund(fund_key) ON DELETE CASCADE,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key) ON DELETE SET NULL
);

-- fact_aum: Assets Under Management
-- Note: This table is created as part of the schema but remains empty due to missing raw AUM data.
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_key INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_key INTEGER NOT NULL,
    date_key INTEGER,
    aum REAL CHECK(aum >= 0),
    FOREIGN KEY (fund_key) REFERENCES dim_fund(fund_key) ON DELETE CASCADE,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key) ON DELETE SET NULL
);

-- --------------------------------------------------------
-- 3. Indexes for Performance Optimization
-- --------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_nav_fund_date ON fact_nav(fund_key, date_key);
CREATE INDEX IF NOT EXISTS idx_fact_transactions_fund_date ON fact_transactions(fund_key, date_key);
CREATE INDEX IF NOT EXISTS idx_fact_performance_fund ON fact_performance(fund_key);
CREATE INDEX IF NOT EXISTS idx_fact_aum_fund ON fact_aum(fund_key);
