"""
========================================================
  Mutual Fund Analytics - Day 4: EDA Execution Script
  File   : scripts/verify_day4.py
  Author : Student Project
  Purpose: Executes all Day 4 calculations and exports 15
           publication-quality charts to the reports/ directory.
========================================================
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams["font.size"] = 10
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9
plt.rcParams["figure.titlesize"] = 14

def main():
    print("Starting Day 4 Exploratory Data Analysis (EDA) execution...")
    
    # Check directories
    os.makedirs("reports", exist_ok=True)
    
    # Load cleaned data
    nav_path = "data/processed/nav_history_cleaned.csv"
    bench_path = "data/processed/nifty_benchmarks_cleaned.csv"
    metadata_path = "data/raw/fund_metadata.csv"
    
    if not os.path.exists(nav_path) or not os.path.exists(bench_path) or not os.path.exists(metadata_path):
        print("Error: Missing required datasets. Make sure Day 3 run completed successfully.")
        return
        
    nav_df = pd.read_csv(nav_path)
    bench_df = pd.read_csv(bench_path)
    metadata_df = pd.read_csv(metadata_path)
    
    # Sort and format dates
    nav_df = nav_df.sort_values(['amfi_code', 'date']).reset_index(drop=True)
    nav_df['date'] = pd.to_datetime(nav_df['date'])
    bench_df['date'] = pd.to_datetime(bench_df['date'])
    bench_df = bench_df.sort_values('date').reset_index(drop=True)
    
    # Correct HDFC Money Market Fund decimal typo before 2015-08-30
    nav_df['nav'] = np.where(
        (nav_df['amfi_code'] == 119092) & (nav_df['date'] < pd.to_datetime('2015-08-30')),
        nav_df['nav'] * 100.0,
        nav_df['nav']
    )
    
    # Calculate daily returns
    nav_df['daily_return'] = nav_df.groupby('amfi_code')['nav'].pct_change()
    
    print("Cleaned datasets loaded. Total NAV records:", len(nav_df))
    
    # ==========================================================================
    # CHART 1: Daily NAV Trends (2022–2026) with highlights
    # ==========================================================================
    print("Generating Chart 1: Daily NAV Trends (2022-2026)...")
    plt.figure(figsize=(12, 6))
    df_2022 = nav_df[nav_df['date'] >= pd.to_datetime('2022-01-01')].copy()
    
    for code in df_2022['amfi_code'].unique():
        fdf = df_2022[df_2022['amfi_code'] == code].sort_values('date')
        name = fdf.iloc[0]['scheme_name'].split('-')[0].strip()
        plt.plot(fdf['date'], fdf['nav'], label=name, linewidth=1.5)
        
    # Highlights
    # 2023 Bull Run: April 2023 to Dec 2023
    plt.axvspan(pd.to_datetime('2023-04-01'), pd.to_datetime('2023-12-31'), 
                color='green', alpha=0.1, label='2023 Bull Run Highlight')
    # 2024 Market Correction: Jan 2024 to June 2024
    plt.axvspan(pd.to_datetime('2024-01-01'), pd.to_datetime('2024-06-15'), 
                color='red', alpha=0.1, label='2024 Correction Highlight')
                
    plt.title("Daily NAV Trends (2022–2026) | Schemes Showcase", fontweight='bold', pad=12)
    plt.xlabel("Timeline", labelpad=8)
    plt.ylabel("Net Asset Value (NAV) in INR", labelpad=8)
    plt.legend(loc="upper left", frameon=True, fontsize=8)
    plt.tight_layout()
    plt.savefig("reports/chart1_nav_trends.png", dpi=300)
    plt.close()
    
    # ==========================================================================
    # CHART 2: Normalized Cumulative Growth Comparison (2013–2026)
    # ==========================================================================
    print("Generating Chart 2: Normalized Cumulative Growth (2013-2026)...")
    plt.figure(figsize=(12, 6))
    
    # Align from 2013-01-02
    start_date = pd.to_datetime('2013-01-02')
    df_post_start = nav_df[nav_df['date'] >= start_date].copy()
    
    for code in df_post_start['amfi_code'].unique():
        fdf = df_post_start[df_post_start['amfi_code'] == code].sort_values('date')
        if fdf.empty:
            continue
        first_nav = fdf['nav'].iloc[0]
        fdf['cum_growth'] = (fdf['nav'] / first_nav) * 100.0
        name = fdf.iloc[0]['scheme_name'].split('-')[0].strip()
        plt.plot(fdf['date'], fdf['cum_growth'], label=name, linewidth=1.5)
        
    plt.title("Normalized Cumulative Growth (2013-2026) | Base = 100", fontweight='bold', pad=12)
    plt.xlabel("Timeline", labelpad=8)
    plt.ylabel("Growth Value", labelpad=8)
    plt.legend(loc="upper left", frameon=True, fontsize=8)
    plt.tight_layout()
    plt.savefig("reports/chart2_cum_growth.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 3: Correlation Matrix Heatmap of Daily Returns
    # ==========================================================================
    print("Generating Chart 3: Correlation Heatmap...")
    pivot_df = nav_df.pivot_table(index='date', columns='scheme_name', values='daily_return')
    pivot_df.columns = [c.split('-')[0].strip() for c in pivot_df.columns]
    corr = pivot_df.corr()
    
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn', vmin=-1, vmax=1, center=0, linewidths=0.5)
    plt.title("Daily Returns Correlation Matrix Between Funds", fontweight='bold', pad=15)
    plt.xticks(rotation=25, ha='right', fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.savefig("reports/chart3_correlation_matrix.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 4: Daily Returns Distribution
    # ==========================================================================
    print("Generating Chart 4: Daily Returns Distribution...")
    plt.figure(figsize=(12, 6))
    
    # Pivot returns and filter out outlier values
    clean_returns = nav_df.dropna(subset=['daily_return']).copy()
    clean_returns = clean_returns[clean_returns['daily_return'].abs() < 0.10]
    
    for code in clean_returns['amfi_code'].unique():
        fdf = clean_returns[clean_returns['amfi_code'] == code]
        name = fdf.iloc[0]['scheme_name'].split('-')[0].strip()
        sns.kdeplot(fdf['daily_return'] * 100.0, label=name, fill=False, linewidth=1.5)
        
    plt.title("Distribution of Daily Returns (Winsorized to [-10%, 10%])", fontweight='bold', pad=12)
    plt.xlabel("Daily Return (%)", labelpad=8)
    plt.ylabel("Density", labelpad=8)
    plt.legend(loc="upper right", frameon=True, fontsize=8)
    plt.tight_layout()
    plt.savefig("reports/chart4_return_distribution.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 5: Rolling Volatility Time-Series (90-day)
    # ==========================================================================
    print("Generating Chart 5: Rolling Volatility...")
    plt.figure(figsize=(12, 6))
    
    for code in nav_df['amfi_code'].unique():
        fdf = nav_df[nav_df['amfi_code'] == code].sort_values('date').copy()
        fdf['rolling_vol'] = fdf['daily_return'].rolling(90).std() * np.sqrt(252) * 100.0
        fdf = fdf.dropna(subset=['rolling_vol'])
        name = fdf.iloc[0]['scheme_name'].split('-')[0].strip()
        plt.plot(fdf['date'], fdf['rolling_vol'], label=name, linewidth=1.2)
        
    plt.title("Annualized 90-Day Rolling Volatility Time-Series", fontweight='bold', pad=12)
    plt.xlabel("Timeline", labelpad=8)
    plt.ylabel("Rolling Volatility (%)", labelpad=8)
    plt.legend(loc="upper right", frameon=True, fontsize=8)
    plt.tight_layout()
    plt.savefig("reports/chart5_rolling_volatility.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 6: Rolling Beta Time-Series (90-day against Nifty 50)
    # ==========================================================================
    print("Generating Chart 6: Rolling Beta...")
    plt.figure(figsize=(12, 6))
    
    for code in nav_df['amfi_code'].unique():
        fdf = nav_df[nav_df['amfi_code'] == code].sort_values('date').copy()
        name = fdf.iloc[0]['scheme_name'].split('-')[0].strip()
        
        # Merge with Nifty 50
        merged = pd.merge(fdf[['date', 'daily_return']], bench_df[['date', '^NSEI_return']], on='date', how='inner').dropna()
        if len(merged) < 100:
            continue
            
        # Rolling covariance and variance
        cov = merged['daily_return'].rolling(90).cov(merged['^NSEI_return'])
        var = merged['^NSEI_return'].rolling(90).var()
        rolling_beta = cov / var
        
        plt.plot(merged.loc[rolling_beta.dropna().index, 'date'], rolling_beta.dropna(), label=name, linewidth=1.2)
        
    plt.title("Rolling 90-Day Beta Sensitivity Time-Series (Against Nifty 50)", fontweight='bold', pad=12)
    plt.xlabel("Timeline", labelpad=8)
    plt.ylabel("Rolling Beta", labelpad=8)
    plt.legend(loc="upper right", frameon=True, fontsize=8)
    plt.tight_layout()
    plt.savefig("reports/chart6_rolling_beta.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 7: Drawdown Time-Series Curves
    # ==========================================================================
    print("Generating Chart 7: Drawdown Curves...")
    plt.figure(figsize=(12, 6))
    
    for code in nav_df['amfi_code'].unique():
        fdf = nav_df[nav_df['amfi_code'] == code].sort_values('date').copy()
        fdf['peak'] = fdf['nav'].cummax()
        fdf['drawdown'] = (fdf['nav'] - fdf['peak']) / fdf['peak'] * 100.0
        name = fdf.iloc[0]['scheme_name'].split('-')[0].strip()
        plt.plot(fdf['date'], fdf['drawdown'], label=name, linewidth=1.0)
        
    plt.title("Historical Drawdown Curves (Decline from Peak %)", fontweight='bold', pad=12)
    plt.xlabel("Timeline", labelpad=8)
    plt.ylabel("Drawdown (%)", labelpad=8)
    plt.legend(loc="lower left", frameon=True, fontsize=8)
    plt.tight_layout()
    plt.savefig("reports/chart7_drawdown_curves.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 8: Risk-Return Scatter Plot
    # ==========================================================================
    print("Generating Chart 8: Risk-Return Scatter Plot...")
    plt.figure(figsize=(10, 7))
    
    scatter_data = []
    latest_date_str = "2026-06-19"
    
    # We find 3-Year CAGR and volatility
    for code in nav_df['amfi_code'].unique():
        fdf = nav_df[nav_df['amfi_code'] == code].sort_values('date').copy()
        name = fdf.iloc[0]['scheme_name'].split('-')[0].strip()
        
        # 3Y CAGR calculation
        target_dt = pd.to_datetime("2023-06-19")
        fdf['date_dt'] = pd.to_datetime(fdf['date'])
        
        # Find Navs
        nav_latest = fdf[fdf['date_dt'] >= pd.to_datetime(latest_date_str)]['nav'].dropna().first_valid_index()
        nav_3y = fdf[fdf['date_dt'] >= target_dt]['nav'].dropna().first_valid_index()
        
        if nav_latest is not None and nav_3y is not None:
            n_end = fdf.loc[nav_latest, 'nav']
            n_start = fdf.loc[nav_3y, 'nav']
            cagr_3y = (n_end / n_start) ** (1.0 / 3.0) - 1.0
        else:
            cagr_3y = np.nan
            
        vol = fdf['daily_return'].std() * np.sqrt(252)
        
        scatter_data.append({
            'name': name,
            'vol': vol * 100.0,
            'cagr': cagr_3y * 100.0
        })
        
    scatter_df = pd.DataFrame(scatter_data).dropna()
    
    plt.scatter(scatter_df['vol'], scatter_df['cagr'], color='#1f77b4', s=100, edgecolors='black', zorder=3)
    for idx, row in scatter_df.iterrows():
        plt.annotate(row['name'], (row['vol'], row['cagr']), textcoords="offset points", 
                     xytext=(0,10), ha='center', fontsize=8, fontweight='bold')
                     
    plt.title("Risk-Return Profile (3-Year CAGR vs. Volatility)", fontweight='bold', pad=12)
    plt.xlabel("Annualized Volatility (%)", labelpad=8)
    plt.ylabel("3-Year CAGR (%)", labelpad=8)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig("reports/chart8_risk_return_frontier.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 9: Monthly Seasonality Heatmap (Nippon Large Cap)
    # ==========================================================================
    print("Generating Chart 9: Monthly Seasonality Heatmap...")
    fdf = nav_df[nav_df['amfi_code'] == 118632].sort_values('date').copy()
    fdf['year'] = fdf['date'].dt.year
    fdf['month'] = fdf['date'].dt.month
    
    # Calculate monthly return as last / first NAV of the month
    monthly_nav = fdf.groupby(['year', 'month'])['nav'].agg(['first', 'last']).reset_index()
    monthly_nav['monthly_return'] = (monthly_nav['last'] / monthly_nav['first'] - 1.0) * 100.0
    
    # Pivot
    monthly_pivot = monthly_nav.pivot(index='year', columns='month', values='monthly_return')
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_pivot.columns = [month_names[m - 1] for m in monthly_pivot.columns]
    
    plt.figure(figsize=(11, 7))
    sns.heatmap(monthly_pivot, annot=True, fmt='.1f', cmap='RdYlGn', center=0, linewidths=0.5, cbar_kws={'label': 'Return (%)'})
    plt.title("Nippon India Large Cap Fund: Monthly Seasonality Returns Heatmap", fontweight='bold', pad=15)
    plt.xlabel("Month", labelpad=8)
    plt.ylabel("Year", labelpad=8)
    plt.tight_layout()
    plt.savefig("reports/chart9_monthly_seasonality.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 10: Outperformance Spread Curve (Nippon vs. Nifty 50)
    # ==========================================================================
    print("Generating Chart 10: Outperformance Spread...")
    fdf = nav_df[nav_df['amfi_code'] == 118632].sort_values('date').copy()
    fdf = fdf[fdf['date'] >= start_date].reset_index(drop=True)
    fdf['cum_growth'] = (fdf['nav'] / fdf['nav'].iloc[0]) * 100.0
    
    # Merge with Nifty 50
    merged = pd.merge(fdf[['date', 'cum_growth']], bench_df[['date', '^NSEI_close']], on='date', how='inner').sort_values('date').reset_index(drop=True)
    merged['bench_cum'] = (merged['^NSEI_close'] / merged['^NSEI_close'].iloc[0]) * 100.0
    merged['spread'] = merged['cum_growth'] - merged['bench_cum']
    
    plt.figure(figsize=(12, 6))
    plt.plot(merged['date'], merged['spread'], color='purple', linewidth=1.5)
    plt.axhline(0, color='black', linestyle='--', linewidth=1.0)
    plt.fill_between(merged['date'], merged['spread'], 0, where=(merged['spread'] >= 0), color='green', alpha=0.1)
    plt.fill_between(merged['date'], merged['spread'], 0, where=(merged['spread'] < 0), color='red', alpha=0.1)
    
    plt.title("Cumulative Outperformance Spread (Nippon Large Cap vs. Nifty 50 Benchmark)", fontweight='bold', pad=12)
    plt.xlabel("Timeline", labelpad=8)
    plt.ylabel("Spread (%)", labelpad=8)
    plt.tight_layout()
    plt.savefig("reports/chart10_outperformance_spread.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 11: Drawdown Boxplots
    # ==========================================================================
    print("Generating Chart 11: Drawdown Boxplots...")
    dd_data = []
    
    for code in nav_df['amfi_code'].unique():
        fdf = nav_df[nav_df['amfi_code'] == code].sort_values('date').copy()
        fdf['peak'] = fdf['nav'].cummax()
        fdf['drawdown'] = (fdf['nav'] - fdf['peak']) / fdf['peak'] * 100.0
        fdf = fdf.dropna(subset=['drawdown'])
        name = fdf.iloc[0]['scheme_name'].split('-')[0].strip()
        
        # Take daily records to build boxplot
        df_f = pd.DataFrame({
            'scheme': name,
            'drawdown': fdf['drawdown']
        })
        dd_data.append(df_f)
        
    dd_all = pd.concat(dd_data, ignore_index=True)
    
    plt.figure(figsize=(12, 7))
    sns.boxplot(data=dd_all, x='scheme', y='drawdown', palette='Set2')
    plt.title("Distribution of Historical Daily Drawdown Depths", fontweight='bold', pad=12)
    plt.xlabel("Mutual Fund Scheme", labelpad=8)
    plt.ylabel("Daily Drawdown (%)", labelpad=8)
    plt.xticks(rotation=20, ha='right', fontsize=8)
    plt.tight_layout()
    plt.savefig("reports/chart11_drawdown_boxplots.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 12: Rolling 90-Day Correlation Time-Series
    # ==========================================================================
    print("Generating Chart 12: Rolling Correlation...")
    plt.figure(figsize=(12, 6))
    
    # Check correlation of equity funds (Nippon Large Cap, quant Mid, SBI Small) against Nifty 50
    equity_codes = [118632, 120841, 125497]
    for code in equity_codes:
        fdf = nav_df[nav_df['amfi_code'] == code].sort_values('date').copy()
        name = fdf.iloc[0]['scheme_name'].split('-')[0].strip()
        
        merged = pd.merge(fdf[['date', 'daily_return']], bench_df[['date', '^NSEI_return']], on='date', how='inner').dropna()
        if len(merged) < 100:
            continue
            
        rolling_corr = merged['daily_return'].rolling(90).corr(merged['^NSEI_return'])
        plt.plot(merged.loc[rolling_corr.dropna().index, 'date'], rolling_corr.dropna(), label=name, linewidth=1.2)
        
    plt.title("Rolling 90-Day Correlation Coefficient Time-Series (Against Nifty 50)", fontweight='bold', pad=12)
    plt.xlabel("Timeline", labelpad=8)
    plt.ylabel("Rolling Correlation (R)", labelpad=8)
    plt.legend(loc="lower left", frameon=True, fontsize=8)
    plt.tight_layout()
    plt.savefig("reports/chart12_rolling_correlation.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 13: Return Autocorrelation Plot (ACF)
    # ==========================================================================
    print("Generating Chart 13: Autocorrelation Plot...")
    fdf = nav_df[nav_df['amfi_code'] == 118632].sort_values('date').copy()
    rets = fdf['daily_return'].dropna()
    
    lags = range(1, 21)
    acf_vals = [rets.autocorr(lag=l) for l in lags]
    
    # 95% Confidence interval bounds (approx: +- 1.96 / sqrt(N))
    n = len(rets)
    conf_bound = 1.96 / np.sqrt(n)
    
    plt.figure(figsize=(10, 5))
    plt.bar(lags, acf_vals, width=0.4, color='royalblue', edgecolor='navy', zorder=3)
    plt.axhline(0, color='black', linestyle='-', linewidth=0.8)
    plt.axhline(conf_bound, color='red', linestyle='--', linewidth=0.8, label='95% Confidence Bounds')
    plt.axhline(-conf_bound, color='red', linestyle='--', linewidth=0.8)
    
    plt.title("Nippon India Large Cap: Autocorrelation (ACF) of Daily Returns (Lags 1-20)", fontweight='bold', pad=12)
    plt.xlabel("Lag Days", labelpad=8)
    plt.ylabel("Autocorrelation Coefficient", labelpad=8)
    plt.xticks(lags)
    plt.legend(loc="upper right", frameon=True, fontsize=8)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig("reports/chart13_return_autocorrelation.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 14: Bivariate Return Scatter Matrix (Pairplot)
    # ==========================================================================
    print("Generating Chart 14: Return Scatter Matrix...")
    # Select 3 equity schemes to avoid crowding the plot
    sub_pivot = pivot_df[['Nippon India Large Cap Fund', 'quant Mid Cap Fund', 'SBI Small Cap Fund']].dropna()
    
    plt.figure(figsize=(10, 10))
    g = sns.pairplot(sub_pivot, kind='scatter', diag_kind='kde', corner=True,
                     plot_kws={'alpha':0.4, 's':10, 'color':'#2b5c8f'},
                     diag_kws={'color':'#2b5c8f'})
    g.figure.suptitle("Bivariate Daily Returns Scatter Matrix (Equity Schemes Showcase)", fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig("reports/chart14_pairplot_returns.png", dpi=300)
    plt.close()

    # ==========================================================================
    # CHART 15: Tail Risk Comparison (Value-at-Risk & Conditional Value-at-Risk)
    # ==========================================================================
    print("Generating Chart 15: Tail Risk Bar Chart...")
    tail_risk_data = []
    
    for code in nav_df['amfi_code'].unique():
        fdf = nav_df[nav_df['amfi_code'] == code].sort_values('date').copy()
        name = fdf.iloc[0]['scheme_name'].split('-')[0].strip()
        rets = fdf['daily_return'].dropna()
        
        # Historical VaR (negative percentile)
        var_95 = -np.percentile(rets, 5) * 100.0
        var_99 = -np.percentile(rets, 1) * 100.0
        
        # Historical CVaR (mean of losses exceeding VaR)
        cvar_95 = -rets[rets <= np.percentile(rets, 5)].mean() * 100.0
        cvar_99 = -rets[rets <= np.percentile(rets, 1)].mean() * 100.0
        
        tail_risk_data.append({
            'Scheme': name,
            '95% VaR': var_95,
            '99% VaR': var_99,
            '95% CVaR': cvar_95,
            '99% CVaR': cvar_99
        })
        
    tail_df = pd.DataFrame(tail_risk_data)
    
    # Pivot to tidy format for plotting
    tidy_tail = pd.melt(tail_df, id_vars=['Scheme'], value_vars=['95% VaR', '99% VaR', '95% CVaR', '99% CVaR'],
                        var_name='Metric', value_name='Loss %')
                        
    plt.figure(figsize=(12, 7))
    sns.barplot(data=tidy_tail, x='Scheme', y='Loss %', hue='Metric', palette='coolwarm')
    plt.title("Tail Risk Profiles Comparison: Daily Value-at-Risk (VaR) & Conditional VaR (CVaR)", fontweight='bold', pad=12)
    plt.xlabel("Mutual Fund Scheme", labelpad=8)
    plt.ylabel("Potential Daily Loss (%)", labelpad=8)
    plt.xticks(rotation=20, ha='right', fontsize=8)
    plt.legend(loc="upper right", frameon=True, fontsize=9)
    plt.tight_layout()
    plt.savefig("reports/chart15_tail_risk_comparison.png", dpi=300)
    plt.close()

    print("\nAll 15 advanced financial charts exported successfully to 'reports/'!")
    print("Day 4 EDA execution completed successfully!")

if __name__ == "__main__":
    main()
