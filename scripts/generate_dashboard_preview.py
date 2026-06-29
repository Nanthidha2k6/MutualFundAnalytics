"""
========================================================
  Mutual Fund Analytics - Day 4: Dashboard Preview Generator
  File   : scripts/generate_dashboard_preview.py
  Author : Student Project
  Purpose: Generates a publication-quality static chart
           representing the core 'Fund Performance' view
           (Volatility vs 3-Year CAGR bubble plot) and saves
           it as reports/dashboard_scorecard_view.png.
========================================================
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    print("Generating dashboard preview chart...")
    os.makedirs("reports", exist_ok=True)
    
    # Load data
    scorecard_path = "data/processed/power_bi/fact_scorecard.csv"
    fund_path = "data/processed/power_bi/dim_fund.csv"
    nav_path = "data/processed/power_bi/fact_nav.csv"
    
    if not os.path.exists(scorecard_path) or not os.path.exists(fund_path):
        print("[ERROR] Data files missing. Make sure export_power_bi_data.py ran successfully.")
        return
        
    scorecard = pd.read_csv(scorecard_path)
    fund = pd.read_csv(fund_path)
    nav = pd.read_csv(nav_path)
    
    # Merge datasets
    scorecard = scorecard.drop(columns=['scheme_name'], errors='ignore')
    df = pd.merge(scorecard, fund, on="amfi_code")
    
    # Calculate Volatility from daily returns
    nav['date'] = pd.to_datetime(nav['date'])
    vols = nav.groupby('amfi_code')['daily_return'].std() * (252 ** 0.5) * 100.0
    vols_df = vols.reset_index().rename(columns={'daily_return': 'volatility'})
    
    df = pd.merge(df, vols_df, on="amfi_code")
    
    # Format and rename columns
    df['cagr_3y_pct'] = df['cagr_3y'] * 100.0
    
    # Setup styling
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 7))
    
    # Determine bubble size based on AUM
    # Handle scale so bubble size is visible and proportional (AUM range: 100 to 45,000 Cr)
    sizes = df['aum_cr'] * 2.0
    
    # Map colors to overall score
    scatter = plt.scatter(
        df['volatility'], 
        df['cagr_3y_pct'], 
        s=sizes, 
        c=df['overall_scorecard_score'], 
        cmap='coolwarm', 
        alpha=0.85, 
        edgecolors='black', 
        linewidths=1,
        zorder=3
    )
    
    # Annotate names
    for idx, row in df.iterrows():
        name = row['scheme_name'].split("-")[0].strip()
        plt.annotate(
            f"{name}\nScore: {row['overall_scorecard_score']:.1f}", 
            (row['volatility'], row['cagr_3y_pct']),
            textcoords="offset points", 
            xytext=(0,15), 
            ha='center', 
            fontsize=8.5, 
            fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3, ec="black", lw=0.5)
        )
        
    # Aesthetics
    plt.title("Day 4 Power BI Blueprint: Fund Performance Reference Visual\n(3-Year CAGR vs. Volatility | Bubble Size = AUM | Color = Score)", 
              fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Annualized Volatility (%)", labelpad=10, fontsize=11, fontweight='semibold')
    plt.ylabel("3-Year CAGR (%)", labelpad=10, fontsize=11, fontweight='semibold')
    
    cbar = plt.colorbar(scatter)
    cbar.set_label("Overall Score (0 - 100)", rotation=270, labelpad=15, fontsize=10, fontweight='semibold')
    
    # Set limit padding
    plt.xlim(df['volatility'].min() - 2.0, df['volatility'].max() + 2.0)
    plt.ylim(df['cagr_3y_pct'].min() - 3.0, df['cagr_3y_pct'].max() + 3.0)
    
    plt.tight_layout()
    plt.savefig("reports/dashboard_scorecard_view.png", dpi=300)
    plt.close()
    print("Reference chart saved successfully as 'reports/dashboard_scorecard_view.png'.")

if __name__ == "__main__":
    main()
