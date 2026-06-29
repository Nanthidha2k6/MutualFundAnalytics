"""
========================================================
  Mutual Fund Analytics - Day 4: Power BI Data Exporter
  File   : scripts/export_power_bi_data.py
  Author : Student Project
  Purpose: Extracts SQLite tables and calculation CSVs,
           structures them into a clean star schema, and
           exports them as Power BI-ready CSV files.
========================================================
"""
import os
import sqlite3
import numpy as np
import pandas as pd

def main():
    print("="*60)
    print("  POWER BI DATA EXPORTER")
    print("="*60)
    
    # Establish folders
    output_dir = "data/processed/power_bi"
    os.makedirs(output_dir, exist_ok=True)
    
    # Database connections
    db_root = "bluestock_mf.db"
    scorecard_csv = "data/processed/fund_scorecard.csv"
    alpha_beta_csv = "data/processed/alpha_beta.csv"
    benchmarks_csv = "data/processed/nifty_benchmarks_cleaned.csv"
    
    if not os.path.exists(db_root):
        print(f"[ERROR] Database {db_root} not found. Run schema and ingestion scripts first.")
        return
        
    conn = sqlite3.connect(db_root)
    
    # --------------------------------------------------------------------------
    # 1. Export dim_fund
    # --------------------------------------------------------------------------
    print("Processing dim_fund...")
    dim_fund = pd.read_sql_query("SELECT amfi_code, scheme_name, fund_house, category, subcategory, risk_grade FROM dim_fund", conn)
    dim_fund.to_csv(os.path.join(output_dir, "dim_fund.csv"), index=False)
    print(f"  [OK] Exported dim_fund.csv ({len(dim_fund)} rows)")
    
    # --------------------------------------------------------------------------
    # 2. Export fact_nav
    # --------------------------------------------------------------------------
    print("Processing fact_nav...")
    fact_nav = pd.read_sql_query("""
        SELECT f.amfi_code, n.nav, d.full_date as date
        FROM fact_nav n
        JOIN dim_fund f ON n.fund_key = f.fund_key
        JOIN dim_date d ON n.date_key = d.date_key
    """, conn)
    
    # Sort and calculate daily returns
    fact_nav['date'] = pd.to_datetime(fact_nav['date'])
    fact_nav = fact_nav.sort_values(['amfi_code', 'date']).reset_index(drop=True)
    
    # Correct HDFC Money Market Fund decimal scaling typo before 2015-08-30
    fact_nav['nav'] = np.where(
        (fact_nav['amfi_code'] == '119092') & (fact_nav['date'] < pd.to_datetime('2015-08-30')),
        fact_nav['nav'] * 100.0,
        fact_nav['nav']
    )
    
    fact_nav['daily_return'] = fact_nav.groupby('amfi_code')['nav'].pct_change()
    fact_nav.to_csv(os.path.join(output_dir, "fact_nav.csv"), index=False)
    print(f"  [OK] Exported fact_nav.csv ({len(fact_nav)} rows)")
    
    # --------------------------------------------------------------------------
    # 3. Export fact_nifty_benchmarks
    # --------------------------------------------------------------------------
    print("Processing fact_nifty_benchmarks...")
    if os.path.exists(benchmarks_csv):
        bench_df = pd.read_csv(benchmarks_csv)
        bench_df['date'] = pd.to_datetime(bench_df['date'])
        
        # Melt Nifty 50 and Nifty 100 columns into a clean long format for Power BI
        nifty50 = bench_df[['date', '^NSEI_close', '^NSEI_return']].copy()
        nifty50.columns = ['date', 'close', 'daily_return']
        nifty50['benchmark_name'] = 'Nifty 50'
        
        nifty100 = bench_df[['date', '^CNX100_close', '^CNX100_return']].copy()
        nifty100.columns = ['date', 'close', 'daily_return']
        nifty100['benchmark_name'] = 'Nifty 100'
        
        fact_benchmarks = pd.concat([nifty50, nifty100], ignore_index=True)
        fact_benchmarks = fact_benchmarks.sort_values(['benchmark_name', 'date']).reset_index(drop=True)
        fact_benchmarks.to_csv(os.path.join(output_dir, "fact_nifty_benchmarks.csv"), index=False)
        print(f"  [OK] Exported fact_nifty_benchmarks.csv ({len(fact_benchmarks)} rows)")
    else:
        print("  [WARN] benchmarks CSV not found. Skipping...")
        
    # --------------------------------------------------------------------------
    # 4. Export fact_scorecard
    # --------------------------------------------------------------------------
    print("Processing fact_scorecard...")
    if os.path.exists(scorecard_csv):
        score_df = pd.read_csv(scorecard_csv)
        # Rename columns to standard formats
        score_df.columns = [c.lower().replace(" ", "_") for c in score_df.columns]
        score_df.to_csv(os.path.join(output_dir, "fact_scorecard.csv"), index=False)
        print(f"  [OK] Exported fact_scorecard.csv ({len(score_df)} rows)")
    else:
        print("  [WARN] Scorecard CSV not found. Skipping...")
        
    # --------------------------------------------------------------------------
    # 5. Export fact_alpha_beta
    # --------------------------------------------------------------------------
    print("Processing fact_alpha_beta...")
    if os.path.exists(alpha_beta_csv):
        ab_df = pd.read_csv(alpha_beta_csv)
        ab_df.columns = [c.lower().replace(" ", "_") for c in ab_df.columns]
        ab_df.to_csv(os.path.join(output_dir, "fact_alpha_beta.csv"), index=False)
        print(f"  [OK] Exported fact_alpha_beta.csv ({len(ab_df)} rows)")
    else:
        print("  [WARN] Alpha/Beta CSV not found. Skipping...")
        
    conn.close()
    print("\n[SUCCESS] All Power BI-ready CSV files exported to data/processed/power_bi/")
    print("="*60)

if __name__ == "__main__":
    main()
