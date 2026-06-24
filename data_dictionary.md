# Data Dictionary - Bluestock Mutual Fund Analytics (Day 2)

This document provides a comprehensive schema description for all cleaned CSV files (saved in `data/processed/`) and all SQLite database tables in `bluestock_mf.db`.

---

## ⚠️ Source Data Constraints & Limitations

Due to the absence of the raw source files `investor_transactions.csv` and `scheme_performance.csv` in the repository's `data/raw/` directory, the corresponding database tables (`fact_transactions`, `fact_performance`, and `fact_aum`) remain empty. This is done to maintain strict data integrity and avoid fabrication of internship deliverables. Details are annotated in the sections below.

---

## 1. Cleaned CSV Files (`data/processed/`)

### A. `fund_master_cleaned.csv`
Derived from `data/raw/fund_master.csv`. Standardizes columns, trims whitespace, and removes duplicate fund records.

| Column Name | Data Type | Business Meaning / Definition | Source Column / Reference | Allowed Values / Constraints |
|---|---|---|---|---|
| `scheme_code` | Integer | Unique identifier for a mutual fund scheme (AMFI Code) | `scheme_code` | 6-digit numeric ID |
| `scheme_name` | String | Full name of the mutual fund scheme | `scheme_name` | Non-empty text |
| `short_name` | String | Short name or display name of the mutual fund | `short_name` | Non-empty text |
| `fund_house` | String | Asset Management Company (AMC) name | `fund_house` | e.g., SBI Mutual Fund, Axis Mutual Fund |
| `category` | String | Broad asset class category | `category` | e.g., Equity, Debt |
| `sub_category` | String | Specific subclass of the fund | `sub_category` | e.g., Large Cap, Money Market, Small Cap |
| `risk_grade` | String | Risk grade or label assigned to the fund | `risk_grade` | e.g., Very High, Moderate |

### B. `nav_history_cleaned.csv`
Derived from `data/raw/live_nav_combined.csv`. Standardizes columns, parses dates, validates NAV, sorts, and daily forward-fills missing NAV values for weekends/holidays per fund.

| Column Name | Data Type | Business Meaning / Definition | Source Column / Reference | Allowed Values / Constraints |
|---|---|---|---|---|
| `amfi_code` | Integer | Unique AMFI scheme code | `scheme_code` | 6-digit numeric ID |
| `scheme_name` | String | Full name of the mutual fund scheme | `scheme_name` | Non-empty text |
| `date` | Date (String) | Calendar date of the NAV record | `date` | Format: `YYYY-MM-DD` |
| `nav` | Float | Net Asset Value (NAV) in INR per unit | `nav` | Real number > 0 |

### C. Fund-Specific Cleaned CSVs (`nav_*_cleaned.csv`)
Individual cleaned NAV histories for the 6 mutual funds (e.g. `nav_118632_nippon_large_cap_cleaned.csv`). 

| Column Name | Data Type | Business Meaning / Definition | Source Column / Reference | Allowed Values / Constraints |
|---|---|---|---|---|
| `amfi_code` | Integer | Unique AMFI scheme code | `scheme_code` | 6-digit numeric ID |
| `scheme_name` | String | Full name of the mutual fund scheme | `scheme_name` | Non-empty text |
| `date` | Date (String) | Date of NAV record | `date` | Format: `YYYY-MM-DD` |
| `nav` | Float | Net Asset Value (NAV) | `nav` | Real number > 0 |

### D. `live_nav_combined_cleaned.csv`
Cleaned version of combined live NAV without daily forward-filling (contains only trading days).

| Column Name | Data Type | Business Meaning / Definition | Source Column / Reference | Allowed Values / Constraints |
|---|---|---|---|---|
| `amfi_code` | Integer | Unique AMFI scheme code | `scheme_code` | 6-digit numeric ID |
| `scheme_name` | String | Full name of the mutual fund scheme | `scheme_name` | Non-empty text |
| `date` | Date (String) | Trading date of NAV record | `date` | Format: `YYYY-MM-DD` |
| `nav` | Float | Net Asset Value (NAV) | `nav` | Real number > 0 |

---

## 2. Database Star Schema Tables (`bluestock_mf.db`)

### A. `dim_fund` (Dimension Table)
Stores mutual fund scheme metadata. Populated from `fund_master_cleaned.csv`.

| Column Name | SQLite Type | Primary / Foreign Key | Business Meaning / Definition | Source File Reference |
|---|---|---|---|---|
| `fund_key` | INTEGER | PRIMARY KEY (Auto-increment) | Surrogate key identifying the mutual fund | Generated |
| `amfi_code` | TEXT | UNIQUE | Unique AMFI scheme code | `fund_master_cleaned.csv (scheme_code)` |
| `scheme_name`| TEXT | - | Full name of the mutual fund scheme | `fund_master_cleaned.csv (scheme_name)` |
| `fund_house` | TEXT | - | Asset Management Company (AMC) | `fund_master_cleaned.csv (fund_house)` |
| `category` | TEXT | - | Broad asset class (e.g. Equity, Debt) | `fund_master_cleaned.csv (category)` |
| `subcategory`| TEXT | - | Subcategory of fund (e.g. Large Cap, Small Cap) | `fund_master_cleaned.csv (sub_category)` |
| `risk_grade` | TEXT | - | Risk grade or label (e.g. Very High, Moderate) | `fund_master_cleaned.csv (risk_grade)` |

### B. `dim_date` (Dimension Table)
Stores calendar date attributes for time-series analysis. Populated from unique dates in `nav_history_cleaned.csv`.

| Column Name | SQLite Type | Primary / Foreign Key | Business Meaning / Definition | Source File Reference |
|---|---|---|---|---|
| `date_key` | INTEGER | PRIMARY KEY | Date key in `YYYYMMDD` format | Generated from date |
| `full_date` | DATE | UNIQUE | Calendar date | `nav_history_cleaned.csv (date)` |
| `day` | INTEGER | - | Day of the month (1-31) | Extracted from date |
| `month` | INTEGER | - | Month number (1-12) | Extracted from date |
| `month_name`| TEXT | - | Month name (e.g., January) | Extracted from date |
| `quarter` | INTEGER | - | Calendar quarter (1-4) | Extracted from date |
| `year` | INTEGER | - | Year (e.g., 2026) | Extracted from date |
| `week_of_year`| INTEGER | - | ISO week number (1-53) | Extracted from date |

### C. `fact_nav` (Fact Table)
Stores daily NAV records for each scheme. Populated from `nav_history_cleaned.csv`.

| Column Name | SQLite Type | Primary / Foreign Key | Business Meaning / Definition | Source File Reference |
|---|---|---|---|---|
| `nav_key` | INTEGER | PRIMARY KEY (Auto-increment) | Surrogate key identifying the NAV fact | Generated |
| `fund_key` | INTEGER | FOREIGN KEY (`dim_fund.fund_key`) | Key linking to the fund details | `nav_history_cleaned.csv (amfi_code)` |
| `date_key` | INTEGER | FOREIGN KEY (`dim_date.date_key`) | Key linking to the date details | `nav_history_cleaned.csv (date)` |
| `nav` | REAL | - | Net Asset Value (NAV) of the fund | `nav_history_cleaned.csv (nav)` |

### D. `fact_transactions` (Fact Table)
*Status: EMPTY / NOT POPULATED due to missing raw source file.*
Stores transaction details (SIP, Lumpsum, Redemption) for investors.

| Column Name | SQLite Type | Primary / Foreign Key | Business Meaning / Definition | Source File Reference |
|---|---|---|---|---|
| `transaction_key` | INTEGER | PRIMARY KEY (Auto-increment) | Surrogate key identifying the transaction | Generated |
| `fund_key` | INTEGER | FOREIGN KEY (`dim_fund.fund_key`) | Key linking to the fund details | `investor_transactions.csv` (Missing) |
| `date_key` | INTEGER | FOREIGN KEY (`dim_date.date_key`) | Key linking to the date details | `investor_transactions.csv` (Missing) |
| `transaction_type`| TEXT | CHECK (SIP, Lumpsum, Redemption) | Type of purchase/redemption | `investor_transactions.csv` (Missing) |
| `amount` | REAL | CHECK (> 0) | Transaction size in INR | `investor_transactions.csv` (Missing) |
| `kyc_status` | TEXT | CHECK (Yes, No, Pending) | KYC compliance status of investor | `investor_transactions.csv` (Missing) |
| `investor_state` | TEXT | - | Investor's state of residence | `investor_transactions.csv` (Missing) |

### E. `fact_performance` (Fact Table)
*Status: EMPTY / NOT POPULATED due to missing raw source file.*
Stores scheme returns and expense ratios.

| Column Name | SQLite Type | Primary / Foreign Key | Business Meaning / Definition | Source File Reference |
|---|---|---|---|---|
| `performance_key` | INTEGER | PRIMARY KEY (Auto-increment) | Surrogate key identifying the performance record | Generated |
| `fund_key` | INTEGER | FOREIGN KEY (`dim_fund.fund_key`) | Key linking to the fund details | `scheme_performance.csv` (Missing) |
| `date_key` | INTEGER | FOREIGN KEY (`dim_date.date_key`) | Key linking to the date details | `scheme_performance.csv` (Missing) |
| `return_1m` | REAL | - | 1-Month cumulative return (%) | `scheme_performance.csv` (Missing) |
| `return_3m` | REAL | - | 3-Month cumulative return (%) | `scheme_performance.csv` (Missing) |
| `return_6m` | REAL | - | 6-Month cumulative return (%) | `scheme_performance.csv` (Missing) |
| `return_1y` | REAL | - | 1-Year cumulative return (%) | `scheme_performance.csv` (Missing) |
| `return_3y` | REAL | - | 3-Year cumulative return (%) | `scheme_performance.csv` (Missing) |
| `return_5y` | REAL | - | 5-Year cumulative return (%) | `scheme_performance.csv` (Missing) |
| `expense_ratio` | REAL | CHECK (0.1 <= val <= 2.5) | Annual fund management expense ratio (%) | `scheme_performance.csv` (Missing) |

### F. `fact_aum` (Fact Table)
*Status: EMPTY / NOT POPULATED due to missing raw source file.*
Stores scheme assets under management.

| Column Name | SQLite Type | Primary / Foreign Key | Business Meaning / Definition | Source File Reference |
|---|---|---|---|---|
| `aum_key` | INTEGER | PRIMARY KEY (Auto-increment) | Surrogate key identifying the AUM record | Generated |
| `fund_key` | INTEGER | FOREIGN KEY (`dim_fund.fund_key`) | Key linking to the fund details | `scheme_performance.csv` (Missing) |
| `date_key` | INTEGER | FOREIGN KEY (`dim_date.date_key`) | Key linking to the date details | `scheme_performance.csv` (Missing) |
| `aum` | REAL | CHECK (>= 0) | Assets Under Management in Crores (INR) | `scheme_performance.csv` (Missing) |
