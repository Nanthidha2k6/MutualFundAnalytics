"""
========================================================
  Mutual Fund Analytics - Day 2: Data Cleaning Pipeline
  File   : scripts/clean_data.py
  Author : Student Project
  Purpose: Parse, sort, deduplicate, validate, and clean
           real CSV files. Handles forward-filling for
           holidays/weekends within each fund group.
========================================================
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Fix UnicodeEncodeError on Windows terminals using CP1252 encoding.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Configuration
SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

def ensure_processed_dir():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def clean_fund_master():
    print("\n--- Cleaning fund_master.csv ---")
    raw_path = RAW_DIR / "fund_master.csv"
    processed_path = PROCESSED_DIR / "fund_master_cleaned.csv"
    
    if not raw_path.exists():
        print(f"[ERROR] Raw fund master not found at {raw_path}")
        return False
        
    df = pd.read_csv(raw_path)
    
    # Standardize column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    
    # Trim whitespace in string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        
    # Remove duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    dupes_removed = initial_rows - len(df)
    
    # Save cleaned
    df.to_csv(processed_path, index=False)
    print(f"[OK] Cleaned fund_master.csv. Rows: {len(df)} (Removed {dupes_removed} duplicates).")
    return True

def clean_nav_history():
    print("\n--- Cleaning live_nav_combined.csv (Outputting to nav_history_cleaned.csv) ---")
    raw_path = RAW_DIR / "live_nav_combined.csv"
    processed_path = PROCESSED_DIR / "nav_history_cleaned.csv"
    
    if not raw_path.exists():
        print(f"[ERROR] Raw combined NAV file not found at {raw_path}")
        return False
        
    df = pd.read_csv(raw_path)
    
    # Normalize columns
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    
    # Map scheme_code to amfi_code
    df = df.rename(columns={"scheme_code": "amfi_code"})
    
    # Parse date column to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    # Drop rows with null dates or null amfi_code
    df = df.dropna(subset=["date", "amfi_code"])
    df["amfi_code"] = df["amfi_code"].astype(int)
    
    # Validate NAV > 0, separate invalid rows
    initial_rows = len(df)
    valid_mask = df["nav"] > 0
    df_invalid = df[~valid_mask]
    df_valid = df[valid_mask]
    
    if not df_invalid.empty:
        print(f"[WARNING] Flagged/Removed {len(df_invalid)} rows with non-positive NAV:")
        for idx, row in df_invalid.head(5).iterrows():
            print(f"  Fund: {row['amfi_code']} | Date: {row['date'].strftime('%Y-%m-%d')} | NAV: {row['nav']}")
        if len(df_invalid) > 5:
            print(f"  ... and {len(df_invalid) - 5} more.")
            
    # Sort and remove duplicates
    df_valid = df_valid.sort_values(["amfi_code", "date"])
    df_valid = df_valid.drop_duplicates(subset=["amfi_code", "date"])
    
    # Forward-fill missing daily NAV values (for weekends and holidays) within each amfi_code group
    cleaned_groups = []
    for amfi_code, group in df_valid.groupby("amfi_code"):
        # Set date as index and reindex to complete calendar days from min to max date
        group_sorted = group.sort_values("date")
        min_date = group_sorted["date"].min()
        max_date = group_sorted["date"].max()
        
        full_date_range = pd.date_range(start=min_date, end=max_date, freq="D")
        
        # Reindex to full daily range
        group_reindexed = group_sorted.set_index("date").reindex(full_date_range)
        group_reindexed.index.name = "date"
        
        # Fill missing fund metadata and forward-fill NAV values
        group_reindexed["amfi_code"] = amfi_code
        group_reindexed["scheme_name"] = group_reindexed["scheme_name"].ffill()
        group_reindexed["nav"] = group_reindexed["nav"].ffill()
        
        group_cleaned = group_reindexed.reset_index()
        cleaned_groups.append(group_cleaned)
        
    df_cleaned = pd.concat(cleaned_groups, ignore_index=True)
    
    # Format date back to string
    df_cleaned["date"] = df_cleaned["date"].dt.strftime("%Y-%m-%d")
    
    # Save cleaned
    df_cleaned.to_csv(processed_path, index=False)
    print(f"[OK] Cleaned NAV history saved. Rows: {len(df_cleaned):,} (Raw rows: {initial_rows:,}, Duplicates/Invalids filtered, Weekends/Holidays forward-filled).")
    return True

def clean_live_nav_combined():
    print("\n--- Cleaning live_nav_combined.csv (Outputting to live_nav_combined_cleaned.csv) ---")
    raw_path = RAW_DIR / "live_nav_combined.csv"
    processed_path = PROCESSED_DIR / "live_nav_combined_cleaned.csv"
    
    if not raw_path.exists():
        return False
        
    df = pd.read_csv(raw_path)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df = df.rename(columns={"scheme_code": "amfi_code"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["date", "amfi_code", "nav"])
    df = df[df["nav"] > 0]
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    df = df.sort_values(["amfi_code", "date"])
    
    df.to_csv(processed_path, index=False)
    # Also save as nav_cleaned.csv to match Day 1 outputs
    df.to_csv(PROCESSED_DIR / "nav_cleaned.csv", index=False)
    print(f"[OK] Cleaned live_nav_combined.csv. Rows: {len(df):,}")
    return True

def clean_individual_fund_csvs():
    print("\n--- Cleaning individual fund-specific NAV CSV files ---")
    raw_files = list(RAW_DIR.glob("nav_*_*.csv"))
    
    cleaned_count = 0
    for path in raw_files:
        if path.name == "live_nav_combined.csv":
            continue
            
        print(f"  Cleaning {path.name} ...")
        df = pd.read_csv(path)
        
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        df = df.rename(columns={"scheme_code": "amfi_code"})
        
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date", "amfi_code", "nav"])
        df = df[df["nav"] > 0]
        
        df = df.sort_values("date").drop_duplicates(subset=["date"])
        
        # Forward fill weekends/holidays for this individual fund
        min_date = df["date"].min()
        max_date = df["date"].max()
        full_range = pd.date_range(start=min_date, end=max_date, freq="D")
        
        df_reindexed = df.set_index("date").reindex(full_range)
        df_reindexed.index.name = "date"
        df_reindexed["amfi_code"] = df_reindexed["amfi_code"].ffill()
        df_reindexed["scheme_name"] = df_reindexed["scheme_name"].ffill()
        df_reindexed["nav"] = df_reindexed["nav"].ffill()
        
        df_cleaned = df_reindexed.reset_index()
        df_cleaned["date"] = df_cleaned["date"].dt.strftime("%Y-%m-%d")
        
        # Build output path
        out_name = path.stem + "_cleaned.csv"
        out_path = PROCESSED_DIR / out_name
        df_cleaned.to_csv(out_path, index=False)
        print(f"    [OK] Saved {out_name}. Rows: {len(df_cleaned):,}")
        cleaned_count += 1
        
    print(f"[OK] Cleaned {cleaned_count} individual fund CSV files.")
    return True

def run_cleaning_pipeline():
    print("="*60)
    print("  STARTING DATA CLEANING PIPELINE")
    print("="*60)
    ensure_processed_dir()
    
    clean_fund_master()
    clean_nav_history()
    clean_live_nav_combined()
    clean_individual_fund_csvs()
    
    print("\n" + "="*60)
    print("  DATA CLEANING PIPELINE COMPLETE")
    print("="*60)

if __name__ == "__main__":
    run_cleaning_pipeline()
