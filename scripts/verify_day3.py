"""
========================================================
  Mutual Fund Analytics - Day 3: Execution Script
  File   : scripts/verify_day3.py
  Author : Student Project
  Purpose: Runs all Day 3 analytics, computes performance
           and risk metrics, linear regressions, drawdowns,
           the scorecard, and outputs data and plots.
========================================================
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress, skew, kurtosis
from datetime import datetime

# Risk-free rate (annualized)
RF_ANNUAL = 0.065
RF_DAILY = RF_ANNUAL / 252

def get_nav_on_date(df_fund, target_date_str):
    """
    Finds the NAV of the fund closest to the target date.
    Returns (nav, date).
    """
    df = df_fund.copy()
    target_dt = pd.to_datetime(target_date_str)
    df['date_dt'] = pd.to_datetime(df['date'])
    diff = (df['date_dt'] - target_dt).abs()
    closest_idx = diff.idxmin()
    if diff.loc[closest_idx].days <= 7:
        return df.loc[closest_idx, 'nav'], df.loc[closest_idx, 'date']
    return None, None

def calculate_cagr(nav_start, nav_end, years):
    if nav_start is None or nav_end is None or nav_start <= 0 or nav_end <= 0:
        return np.nan
    return (nav_end / nav_start) ** (1.0 / years) - 1.0

def calculate_downside_deviation(returns, target_rate=RF_DAILY):
    """
    Computes annualized downside deviation (for Sortino ratio).
    """
    excess_returns = returns - target_rate
    downside_returns = np.minimum(0, excess_returns)
    downside_var = np.mean(downside_returns ** 2)
    return np.sqrt(downside_var) * np.sqrt(252)

def calculate_drawdown_periods(df_fund):
    """
    Finds the max drawdown and details of the worst drawdown period.
    """
    df = df_fund.copy().sort_values('date').reset_index(drop=True)
    df['peak'] = df['nav'].cummax()
    df['drawdown'] = (df['nav'] - df['peak']) / df['peak']
    
    max_dd = df['drawdown'].min()
    if pd.isna(max_dd) or max_dd == 0:
        return 0.0, "N/A", "N/A", "N/A"
        
    trough_idx = df['drawdown'].idxmin()
    trough_date = df.loc[trough_idx, 'date']
    
    peak_idx = df.loc[:trough_idx, 'nav'].idxmax()
    peak_date = df.loc[peak_idx, 'date']
    
    recovery_df = df.loc[trough_idx:]
    recovered_runs = recovery_df[recovery_df['nav'] >= df.loc[peak_idx, 'nav']]
    if not recovered_runs.empty:
        recovery_idx = recovered_runs.index[0]
        recovery_date = df.loc[recovery_idx, 'date']
    else:
        recovery_date = "Unrecovered"
        
    return max_dd, peak_date, trough_date, recovery_date

def main():
    print("Starting Day 3 performance and risk analytics...")
    
    # 1. Check directories
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # 2. Load cleaned data
    nav_history_path = "data/processed/nav_history_cleaned.csv"
    fund_metadata_path = "data/raw/fund_metadata.csv"
    benchmarks_path = "data/processed/nifty_benchmarks_cleaned.csv"
    
    if not os.path.exists(nav_history_path):
        raise FileNotFoundError(f"Missing {nav_history_path}")
    if not os.path.exists(fund_metadata_path):
        raise FileNotFoundError(f"Missing {fund_metadata_path}")
    if not os.path.exists(benchmarks_path):
        raise FileNotFoundError(f"Missing {benchmarks_path}")
        
    nav_df = pd.read_csv(nav_history_path)
    metadata_df = pd.read_csv(fund_metadata_path)
    bench_df = pd.read_csv(benchmarks_path)
    
    # Sort data
    nav_df = nav_df.sort_values(['amfi_code', 'date']).reset_index(drop=True)
    nav_df['date'] = pd.to_datetime(nav_df['date']).dt.strftime('%Y-%m-%d')
    bench_df['date'] = pd.to_datetime(bench_df['date']).dt.strftime('%Y-%m-%d')
    
    # Correct HDFC Money Market Fund decimal typo before 2015-08-30
    nav_df['nav'] = np.where(
        (nav_df['amfi_code'] == 119092) & (nav_df['date'] < '2015-08-30'),
        nav_df['nav'] * 100.0,
        nav_df['nav']
    )
    
    # 3. Calculate daily returns
    nav_df['daily_return'] = nav_df.groupby('amfi_code')['nav'].pct_change()
    
    # Prepare scorecard list
    scorecard_data = []
    alpha_beta_data = []
    
    # Group by fund
    grouped = nav_df.groupby('amfi_code')
    latest_date_str = "2026-06-19"
    
    print("\nProcessing individual mutual funds:")
    for amfi_code, df_fund in grouped:
        df_fund = df_fund.dropna(subset=['nav']).sort_values('date').reset_index(drop=True)
        scheme_name = df_fund.loc[0, 'scheme_name']
        print(f"\n- Fund: {scheme_name} (AMFI: {amfi_code})")
        
        # Get metadata
        fund_meta = metadata_df[metadata_df['scheme_code'] == amfi_code]
        if fund_meta.empty:
            print(f"  [Warning] No metadata found for AMFI {amfi_code}. Skipping AUM/Expense metrics.")
            aum = np.nan
            expense_ratio = np.nan
            bench_ticker = "^NSEI" # default benchmark
        else:
            fund_meta = fund_meta.iloc[0]
            aum = fund_meta['aum_cr']
            expense_ratio = fund_meta['expense_ratio_percent']
            # Determine benchmark mapping based on metadata or name
            if "quant Mid" in scheme_name or "SBI Small" in scheme_name:
                bench_ticker = "^CNX100"
            else:
                bench_ticker = "^NSEI"
                
        # Latest NAV details
        nav_latest, date_latest = get_nav_on_date(df_fund, latest_date_str)
        if nav_latest is None:
            print(f"  [Error] No latest NAV data near {latest_date_str} for {scheme_name}. Skipping.")
            continue
            
        # Get start NAVs for CAGR (1Y, 3Y, 5Y)
        nav_1y, date_1y = get_nav_on_date(df_fund, "2025-06-19")
        nav_3y, date_3y = get_nav_on_date(df_fund, "2023-06-19")
        nav_5y, date_5y = get_nav_on_date(df_fund, "2021-06-19")
        
        cagr_1y = calculate_cagr(nav_1y, nav_latest, 1.0)
        cagr_3y = calculate_cagr(nav_3y, nav_latest, 3.0)
        cagr_5y = calculate_cagr(nav_5y, nav_latest, 5.0)
        
        print(f"  CAGR 1Y: {cagr_1y*100:.2f}% (from {date_1y})")
        print(f"  CAGR 3Y: {cagr_3y*100:.2f}% (from {date_3y})")
        print(f"  CAGR 5Y: {cagr_5y*100:.2f}% (from {date_5y})")
        
        # Daily return stats
        fund_returns = df_fund['daily_return'].dropna()
        mean_ret = fund_returns.mean()
        std_ret = fund_returns.std()
        
        # Annualized metrics
        ann_return = mean_ret * 252
        ann_vol = std_ret * np.sqrt(252)
        
        sharpe = (ann_return - RF_ANNUAL) / ann_vol if ann_vol > 0 else np.nan
        downside_dev = calculate_downside_deviation(fund_returns)
        sortino = (ann_return - RF_ANNUAL) / downside_dev if downside_dev > 0 else np.nan
        
        print(f"  Sharpe Ratio: {sharpe:.4f}")
        print(f"  Sortino Ratio: {sortino:.4f}")
        
        # Drawdowns
        max_dd, peak_date, trough_date, recovery_date = calculate_drawdown_periods(df_fund)
        print(f"  Max Drawdown: {max_dd*100:.2f}% (Peak: {peak_date}, Trough: {trough_date}, Recovery: {recovery_date})")
        
        # Return distribution validation
        skewness_val = skew(fund_returns)
        kurtosis_val = kurtosis(fund_returns)
        print(f"  Distribution: Mean={mean_ret*100:.4f}%, Std={std_ret*100:.4f}%, Skew={skewness_val:.4f}, Kurt={kurtosis_val:.4f}")
        
        fund_ret_df = df_fund[['date', 'daily_return']].dropna()
        merged_bench = pd.merge(fund_ret_df, bench_df[['date', f'{bench_ticker}_return']], on='date', how='inner').dropna()
        
        if not merged_bench.empty:
            bench_ret_series = merged_bench[f'{bench_ticker}_return']
            fund_ret_series = merged_bench['daily_return']
            
            # Regression
            slope, intercept, r_value, p_value, std_err = linregress(bench_ret_series, fund_ret_series)
            beta = slope
            daily_alpha = intercept
            ann_alpha = daily_alpha * 252
            
            # Tracking Error
            tracking_error = np.std(fund_ret_series - bench_ret_series) * np.sqrt(252)
            
            print(f"  Benchmark: {bench_ticker} | Beta: {beta:.4f} | Alpha (Ann): {ann_alpha*100:.2f}% | Tracking Error: {tracking_error*100:.2f}%")
            
            alpha_beta_data.append({
                "amfi_code": amfi_code,
                "scheme_name": scheme_name,
                "benchmark": bench_ticker,
                "alpha_annualized": ann_alpha,
                "beta": beta,
                "tracking_error_annualized": tracking_error
            })
        else:
            print("  [Error] No overlapping date records for benchmark regression.")
            beta, ann_alpha, tracking_error = np.nan, np.nan, np.nan
            
        # Append to scorecard base table
        scorecard_data.append({
            "amfi_code": amfi_code,
            "scheme_name": scheme_name,
            "cagr_1y": cagr_1y,
            "cagr_3y": cagr_3y,
            "cagr_5y": cagr_5y,
            "volatility_annualized": ann_vol,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "max_drawdown": max_dd,
            "worst_dd_peak_date": peak_date,
            "worst_dd_trough_date": trough_date,
            "worst_dd_recovery_date": recovery_date,
            "aum_cr": aum,
            "expense_ratio_percent": expense_ratio,
            "skewness": skewness_val,
            "kurtosis": kurtosis_val
        })
        
    # --- Scorecard Scoring Algorithm (0-100) ---
    print("\nCalculating Scorecard Scores...")
    score_df = pd.DataFrame(scorecard_data)
    
    # Min-max scaling functions
    def scale_higher_better(series):
        s_min = series.min()
        s_max = series.max()
        if s_max == s_min:
            return pd.Series(100.0, index=series.index)
        return (series - s_min) / (s_max - s_min) * 100.0

    def scale_lower_better(series):
        s_min = series.min()
        s_max = series.max()
        if s_max == s_min:
            return pd.Series(100.0, index=series.index)
        return (s_max - series) / (s_max - s_min) * 100.0

    # Handle scores for each metric
    score_df['score_cagr_3y'] = scale_higher_better(score_df['cagr_3y'])
    score_df['score_sharpe'] = scale_higher_better(score_df['sharpe_ratio'])
    score_df['score_sortino'] = scale_higher_better(score_df['sortino_ratio'])
    # Drawdowns are negative numbers, so higher drawdown (closer to 0) is better.
    score_df['score_drawdown'] = scale_higher_better(score_df['max_drawdown'])
    score_df['score_expense'] = scale_lower_better(score_df['expense_ratio_percent'])
    
    # Base weights
    base_weights = {
        'score_cagr_3y': 0.30,
        'score_sharpe': 0.25,
        'score_sortino': 0.20,
        'score_drawdown': 0.15,
        'score_expense': 0.10
    }
    
    # Calculate weighted rescaled scorecard score for each fund
    final_scores = []
    audit_logs = []
    
    for idx, row in score_df.iterrows():
        total_weight = 0.0
        weighted_sum = 0.0
        omitted = []
        
        # Check cagr_3y
        if not pd.isna(row['cagr_3y']):
            total_weight += base_weights['score_cagr_3y']
            weighted_sum += row['score_cagr_3y'] * base_weights['score_cagr_3y']
        else:
            omitted.append("3-Year CAGR")
            
        # Check sharpe
        if not pd.isna(row['sharpe_ratio']):
            total_weight += base_weights['score_sharpe']
            weighted_sum += row['score_sharpe'] * base_weights['score_sharpe']
        else:
            omitted.append("Sharpe Ratio")
            
        # Check sortino
        if not pd.isna(row['sortino_ratio']):
            total_weight += base_weights['score_sortino']
            weighted_sum += row['score_sortino'] * base_weights['score_sortino']
        else:
            omitted.append("Sortino Ratio")
            
        # Check drawdown
        if not pd.isna(row['max_drawdown']):
            total_weight += base_weights['score_drawdown']
            weighted_sum += row['score_drawdown'] * base_weights['score_drawdown']
        else:
            omitted.append("Max Drawdown")
            
        # Check expense ratio
        if not pd.isna(row['expense_ratio_percent']):
            total_weight += base_weights['score_expense']
            weighted_sum += row['score_expense'] * base_weights['score_expense']
        else:
            omitted.append("Expense Ratio")
            
        if total_weight > 0:
            final_score = weighted_sum / total_weight
        else:
            final_score = np.nan
            
        final_scores.append(round(final_score, 2))
        audit_logs.append(", ".join(omitted) if omitted else "None")
        
    score_df['overall_scorecard_score'] = final_scores
    score_df['omitted_metrics'] = audit_logs
    
    # Drop intermediate scoring columns for output
    cols_to_keep = [
        "amfi_code", "scheme_name", "cagr_1y", "cagr_3y", "cagr_5y", 
        "volatility_annualized", "sharpe_ratio", "sortino_ratio", "max_drawdown", 
        "worst_dd_peak_date", "worst_dd_trough_date", "worst_dd_recovery_date", 
        "aum_cr", "expense_ratio_percent", "skewness", "kurtosis",
        "overall_scorecard_score", "omitted_metrics"
    ]
    final_score_df = score_df[cols_to_keep]
    
    # Save processed CSVs
    final_score_df.to_csv("data/processed/fund_scorecard.csv", index=False)
    print("Saved fund scorecard to data/processed/fund_scorecard.csv")
    
    alpha_beta_df = pd.DataFrame(alpha_beta_data)
    alpha_beta_df.to_csv("data/processed/alpha_beta.csv", index=False)
    print("Saved alpha beta calculations to data/processed/alpha_beta.csv")
    
    # Print summary table to stdout
    print("\n" + "="*80)
    print(f"{'DAY 3 FUND SCORECARD RESULTS':^80}")
    print("="*80)
    print(final_score_df[['scheme_name', 'cagr_3y', 'sharpe_ratio', 'max_drawdown', 'expense_ratio_percent', 'overall_scorecard_score']].to_string(index=False))
    print("="*80)
    
    # --- Generate Chart: Cumulative Returns Comparison ---
    print("\nGenerating benchmark comparison chart...")
    plt.figure(figsize=(12, 7))
    
    # We want to plot Nippon Large Cap (118632), Quant Mid Cap (120841), SBI Small Cap (125497)
    # and overlay benchmarks Nifty 50 and Nifty 100
    plot_codes = [118632, 120841, 125497]
    colors = {
        118632: '#1f77b4',  # Sleek blue
        120841: '#d62728',  # Sleek red
        125497: '#2ca02c',  # Sleek green
        '^NSEI': '#ff7f0e', # Orange
        '^CNX100': '#9467bd' # Purple
    }
    
    # Plot benchmarks
    bench_plot_df = bench_df.copy().sort_values('date').reset_index(drop=True)
    bench_plot_df = bench_plot_df[bench_plot_df['date'] >= '2013-01-02']
    
    for ticker, label in [('^NSEI', 'Nifty 50 Benchmark'), ('^CNX100', 'Nifty 100 Benchmark')]:
        close_col = f"{ticker}_close"
        # Cumulative performance: Base 100
        first_val = bench_plot_df[close_col].iloc[0]
        bench_plot_df[f'{ticker}_cum'] = (bench_plot_df[close_col] / first_val) * 100.0
        plt.plot(pd.to_datetime(bench_plot_df['date']), bench_plot_df[f'{ticker}_cum'], 
                 label=label, color=colors[ticker], linewidth=1.5, linestyle='--')
        
    # Plot funds
    for code in plot_codes:
        df_f = nav_df[nav_df['amfi_code'] == code].copy().sort_values('date').reset_index(drop=True)
        df_f = df_f[df_f['date'] >= '2013-01-02']
        if df_f.empty:
            continue
        first_nav = df_f['nav'].iloc[0]
        df_f['cum_nav'] = (df_f['nav'] / first_nav) * 100.0
        name = df_f.loc[0, 'scheme_name'].split('-')[0].strip()
        plt.plot(pd.to_datetime(df_f['date']), df_f['cum_nav'], 
                 label=name, color=colors[code], linewidth=2.0)
        
    plt.title("Cumulative Growth of Normalized Base (100) | Funds vs Benchmarks (2013-2026)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Timeline", fontsize=12, labelpad=10)
    plt.ylabel("Growth Value (Base = 100)", fontsize=12, labelpad=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='#e0e0e0', framealpha=0.9, fontsize=10)
    
    # Modern styling
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.tight_layout()
    
    chart_path = "reports/benchmark_comparison.png"
    plt.savefig(chart_path, dpi=300)
    # Load into SQLite database
    import sqlite3
    db_path = "data/processed/mutual_funds.db"
    if os.path.exists(db_path):
        print(f"Loading Day 3 results into SQLite database: {db_path}...")
        conn = sqlite3.connect(db_path)
        final_score_df.to_sql("fund_scorecard", conn, if_exists="replace", index=False)
        alpha_beta_df.to_sql("alpha_beta", conn, if_exists="replace", index=False)
        bench_df.to_sql("nifty_benchmarks", conn, if_exists="replace", index=False)
        conn.close()
        print("Successfully loaded scorecard, alpha_beta, and nifty_benchmarks tables.")
        
    print("\nDay 3 Performance and Risk Analytics completed successfully!")

if __name__ == "__main__":
    main()
