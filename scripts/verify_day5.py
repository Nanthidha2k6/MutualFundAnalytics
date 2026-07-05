"""
========================================================
  Mutual Fund Analytics - Day 5: Advanced Analytics Execution
  File   : scripts/verify_day5.py
  Author : Student Project
  Purpose: Executes VaR/CVaR risk calculations, exports
           rolling Sharpe charts, and writes report files.
========================================================
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    print("="*60)
    print("  DAY 5 ADVANCED ANALYTICS RUNNER")
    print("="*60)
    
    # Establish directories
    os.makedirs("reports", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    # Load data
    nav_path = "data/processed/power_bi/fact_nav.csv"
    fund_path = "data/processed/power_bi/dim_fund.csv"
    
    if not os.path.exists(nav_path) or not os.path.exists(fund_path):
        print("[ERROR] Missing Power BI-ready CSV files in data/processed/power_bi/")
        return
        
    nav_df = pd.read_csv(nav_path)
    fund_df = pd.read_csv(fund_path)
    
    # Sort and format dates
    nav_df['date'] = pd.to_datetime(nav_df['date'])
    nav_df = nav_df.sort_values(['amfi_code', 'date']).reset_index(drop=True)
    
    # Calculate daily returns if any are null
    nav_df['daily_return'] = nav_df.groupby('amfi_code')['nav'].pct_change()
    
    # --------------------------------------------------------------------------
    # Task 1: Historical VaR (95%) & CVaR (Expected Shortfall)
    # --------------------------------------------------------------------------
    print("Executing Task 1: Historical VaR & CVaR...")
    var_cvar_records = []
    
    for code in nav_df['amfi_code'].unique():
        fdf = nav_df[nav_df['amfi_code'] == code].dropna(subset=['daily_return'])
        name = fund_df[fund_df['amfi_code'] == code]['scheme_name'].values[0]
        rets = fdf['daily_return']
        
        # 95% Historical VaR
        cutoff_95 = np.percentile(rets, 5)
        var_95_pct = -cutoff_95 * 100.0
        
        # 95% CVaR (Expected Shortfall)
        cvar_95_pct = -rets[rets <= cutoff_95].mean() * 100.0
        
        var_cvar_records.append({
            'amfi_code': code,
            'scheme_name': name,
            'var_95_pct': var_95_pct,
            'cvar_95_pct': cvar_95_pct
        })
        
    var_cvar_df = pd.DataFrame(var_cvar_records)
    report_path = "data/processed/var_cvar_report.csv"
    var_cvar_df.to_csv(report_path, index=False)
    print(f"  [OK] Exported {report_path} ({len(var_cvar_df)} rows)")
    print(var_cvar_df)
    
    # --------------------------------------------------------------------------
    # Task 2: Rolling 90-Day Sharpe Ratio
    # --------------------------------------------------------------------------
    print("\nExecuting Task 2: Rolling 90-Day Sharpe Ratio...")
    
    # Annualized Risk-Free Rate = 6.5%, Daily RF = 0.065 / 252
    rf_daily = 0.065 / 252
    
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 6))
    
    for code in nav_df['amfi_code'].unique():
        fdf = nav_df[nav_df['amfi_code'] == code].sort_values('date').copy()
        name = fund_df[fund_df['amfi_code'] == code]['scheme_name'].values[0].split("-")[0].strip()
        
        # Calculate daily excess returns
        fdf['excess_return'] = fdf['daily_return'] - rf_daily
        
        # Rolling 90-day mean of excess returns
        rolling_mean_excess = fdf['excess_return'].rolling(90).mean()
        # Rolling 90-day standard deviation of daily returns
        rolling_std = fdf['daily_return'].rolling(90).std()
        
        # Annualized rolling Sharpe Ratio
        rolling_sharpe = (rolling_mean_excess / rolling_std) * np.sqrt(252)
        
        plt.plot(fdf['date'], rolling_sharpe, label=name, linewidth=1.2)
        
    plt.title("Rolling 90-Day Annualized Sharpe Ratio Time-Series (Rf = 6.5%)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Timeline", labelpad=8)
    plt.ylabel("Rolling Sharpe Ratio", labelpad=8)
    plt.legend(loc="upper right", frameon=True, fontsize=8)
    plt.tight_layout()
    
    chart_path = "reports/rolling_sharpe_chart.png"
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"  [OK] Saved {chart_path}")
    print("="*60)
    print("Day 5 risk calculations completed successfully!")

if __name__ == "__main__":
    main()
