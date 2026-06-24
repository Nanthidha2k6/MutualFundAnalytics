"""
========================================================
  Mutual Fund Analytics - Day 2: Database Loader
  File   : sql/load_cleaned_data.py
  Author : Student Project
  Purpose: Load cleaned CSV files into the SQLite star schema
           database using SQLAlchemy and Pandas.
========================================================
"""

import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

# Fix UnicodeEncodeError on Windows terminals using CP1252 encoding.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Configuration
SQL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SQL_DIR.parent
DB_PATH = PROJECT_ROOT / "bluestock_mf.db"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

def load_data():
    print("="*60)
    print("  STARTING DATABASE LOADING PIPELINE")
    print("="*60)
    print(f"Target Database: {DB_PATH.resolve()}")
    print(f"Source Folder  : {PROCESSED_DIR.resolve()}")
    
    if not DB_PATH.exists():
        print(f"[ERROR] Database file does not exist. Run create_schema.py first.")
        sys.exit(1)
        
    db_uri = f"sqlite:///{DB_PATH.resolve()}"
    engine = create_engine(db_uri)
    
    # Establish connection and ensure foreign keys are enabled
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON;"))
        
    # --------------------------------------------------------
    # 1. Populate Dimension: dim_fund
    # --------------------------------------------------------
    print("\n--- Seeding dim_fund ---")
    fm_cleaned_path = PROCESSED_DIR / "fund_master_cleaned.csv"
    
    if not fm_cleaned_path.exists():
        print(f"[ERROR] Cleaned fund master not found at {fm_cleaned_path}")
        sys.exit(1)
        
    df_fm = pd.read_csv(fm_cleaned_path)
    
    # Map CSV columns to dim_fund table columns:
    # scheme_code -> amfi_code
    # sub_category -> subcategory
    df_fund_dim = pd.DataFrame()
    df_fund_dim["amfi_code"] = df_fm["scheme_code"].astype(str).str.strip()
    df_fund_dim["scheme_name"] = df_fm["scheme_name"].astype(str).str.strip()
    df_fund_dim["fund_house"] = df_fm["fund_house"].astype(str).str.strip()
    df_fund_dim["category"] = df_fm["category"].astype(str).str.strip()
    df_fund_dim["subcategory"] = df_fm["sub_category"].astype(str).str.strip()
    df_fund_dim["risk_grade"] = df_fm["risk_grade"].astype(str).str.strip()
    
    df_fund_dim = df_fund_dim.drop_duplicates(subset=["amfi_code"])
    
    try:
        # Clear existing data in dim_fund (if any) and append
        with engine.begin() as conn:
            # Temporarily disable foreign key checks for clearing tables
            conn.execute(text("PRAGMA foreign_keys = OFF;"))
            conn.execute(text("DELETE FROM dim_fund;"))
            conn.execute(text("PRAGMA foreign_keys = ON;"))
            
        df_fund_dim.to_sql(name="dim_fund", con=engine, if_exists="append", index=False)
        print(f"  [OK] Successfully loaded {len(df_fund_dim)} rows into dim_fund.")
    except Exception as exc:
        print(f"  [FAIL] Failed to load dim_fund: {exc}")
        sys.exit(1)
        
    # --------------------------------------------------------
    # 2. Populate Dimension: dim_date
    # --------------------------------------------------------
    print("\n--- Seeding dim_date ---")
    nav_history_path = PROCESSED_DIR / "nav_history_cleaned.csv"
    
    if not nav_history_path.exists():
        print(f"[ERROR] Cleaned NAV history not found at {nav_history_path}")
        sys.exit(1)
        
    df_nav_history = pd.read_csv(nav_history_path)
    
    # Extract unique dates
    unique_dates = pd.to_datetime(df_nav_history["date"]).drop_duplicates().sort_values()
    
    # Construct date dimension columns
    df_date_dim = pd.DataFrame()
    df_date_dim["full_date"] = unique_dates
    # date_key as YYYYMMDD integer
    df_date_dim["date_key"] = df_date_dim["full_date"].dt.strftime("%Y%m%d").astype(int)
    df_date_dim["day"] = df_date_dim["full_date"].dt.day
    df_date_dim["month"] = df_date_dim["full_date"].dt.month
    df_date_dim["month_name"] = df_date_dim["full_date"].dt.month_name()
    df_date_dim["quarter"] = df_date_dim["full_date"].dt.quarter
    df_date_dim["year"] = df_date_dim["full_date"].dt.year
    df_date_dim["week_of_year"] = df_date_dim["full_date"].dt.isocalendar().week.astype(int)
    
    # Convert full_date column to string format YYYY-MM-DD for database consistency
    df_date_dim["full_date"] = df_date_dim["full_date"].dt.strftime("%Y-%m-%d")
    
    try:
        with engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys = OFF;"))
            conn.execute(text("DELETE FROM dim_date;"))
            conn.execute(text("PRAGMA foreign_keys = ON;"))
            
        df_date_dim.to_sql(name="dim_date", con=engine, if_exists="append", index=False)
        print(f"  [OK] Successfully loaded {len(df_date_dim)} rows into dim_date.")
    except Exception as exc:
        print(f"  [FAIL] Failed to load dim_date: {exc}")
        sys.exit(1)
        
    # --------------------------------------------------------
    # 3. Populate Fact: fact_nav
    # --------------------------------------------------------
    print("\n--- Seeding fact_nav ---")
    
    # Read dim_fund mapping from database to resolve amfi_code -> fund_key
    df_funds_db = pd.read_sql_query("SELECT fund_key, amfi_code FROM dim_fund;", engine)
    fund_map = df_funds_db.set_index("amfi_code")["fund_key"].to_dict()
    
    # Process fact rows
    df_fact_nav = pd.DataFrame()
    
    # Map amfi_code to fund_key
    df_nav_history["amfi_code"] = df_nav_history["amfi_code"].astype(str).str.strip()
    df_fact_nav["fund_key"] = df_nav_history["amfi_code"].map(fund_map)
    
    # Check for unmapped funds
    unmapped_funds = df_fact_nav[df_fact_nav["fund_key"].isna()]["fund_key"]
    if len(unmapped_funds) > 0:
        print(f"  [WARNING] Found {len(unmapped_funds)} rows in NAV history with unmapped AMFI codes!")
        
    # Map date to date_key
    df_fact_nav["date_key"] = pd.to_datetime(df_nav_history["date"]).dt.strftime("%Y%m%d").astype(int)
    df_fact_nav["nav"] = df_nav_history["nav"]
    
    # Drop rows where keys couldn't be resolved
    df_fact_nav = df_fact_nav.dropna(subset=["fund_key", "date_key"])
    df_fact_nav["fund_key"] = df_fact_nav["fund_key"].astype(int)
    
    try:
        with engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys = OFF;"))
            conn.execute(text("DELETE FROM fact_nav;"))
            conn.execute(text("PRAGMA foreign_keys = ON;"))
            
        df_fact_nav.to_sql(name="fact_nav", con=engine, if_exists="append", index=False, chunksize=5000)
        print(f"  [OK] Successfully loaded {len(df_fact_nav)} rows into fact_nav.")
    except Exception as exc:
        print(f"  [FAIL] Failed to load fact_nav: {exc}")
        sys.exit(1)
        
    # --------------------------------------------------------
    # 4. Populate Empty Facts (Due to Missing Raw Source Files)
    # --------------------------------------------------------
    print("\n--- Seeding fact_transactions, fact_performance, fact_aum ---")
    print("  [INFO] The source files 'investor_transactions.csv' and 'scheme_performance.csv'")
    print("         were not provided in the raw directory (data/raw/).")
    print("         In alignment with the strict data integrity guidelines, these tables")
    print("         will remain empty (0 rows loaded).")
    
    # Clear tables to ensure they are empty
    try:
        with engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys = OFF;"))
            conn.execute(text("DELETE FROM fact_transactions;"))
            conn.execute(text("DELETE FROM fact_performance;"))
            conn.execute(text("DELETE FROM fact_aum;"))
            conn.execute(text("PRAGMA foreign_keys = ON;"))
        print("  [OK] Cleared transaction, performance, and AUM fact tables (verified empty).")
    except Exception as exc:
        print(f"  [WARNING] Failed to clear empty tables: {exc}")

    # --------------------------------------------------------
    # 5. Print Loading Summary & Validate
    # --------------------------------------------------------
    print("\n" + "="*50)
    print("  DATABASE LOADING PIPELINE SUMMARY")
    print("="*50)
    
    # Queries to check database counts
    table_counts = {}
    with engine.connect() as conn:
        for table in ["dim_fund", "dim_date", "fact_nav", "fact_transactions", "fact_performance", "fact_aum"]:
            cnt = conn.execute(text(f"SELECT COUNT(*) FROM {table};")).fetchone()[0]
            table_counts[table] = cnt
            
    print(f"  dim_fund (Dimensions)       : {table_counts['dim_fund']:>6,} rows")
    print(f"  dim_date (Dimensions)       : {table_counts['dim_date']:>6,} rows")
    print(f"  fact_nav (NAV Facts)        : {table_counts['fact_nav']:>6,} rows")
    print(f"  fact_transactions (Tx Facts): {table_counts['fact_transactions']:>6,} rows  [EMPTY - Missing source CSV]")
    print(f"  fact_performance (Perf Facts): {table_counts['fact_performance']:>6,} rows  [EMPTY - Missing source CSV]")
    print(f"  fact_aum (AUM Facts)        : {table_counts['fact_aum']:>6,} rows  [EMPTY - Missing source CSV]")
    print("-"*50)
    
    # Validation assertions
    assert table_counts["dim_fund"] == len(df_fund_dim), "dim_fund row count mismatch!"
    assert table_counts["dim_date"] == len(df_date_dim), "dim_date row count mismatch!"
    assert table_counts["fact_nav"] == len(df_fact_nav), "fact_nav row count mismatch!"
    print("  [SUCCESS] All loaded row counts verified successfully.")
    print("="*50)

if __name__ == "__main__":
    load_data()
