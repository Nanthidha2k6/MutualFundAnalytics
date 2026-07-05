"""
========================================================
  Mutual Fund Analytics - Day 5: Fund Recommender Engine
  File   : scripts/recommender.py
  Author : Student Project
  Purpose: CLI tool to recommend top mutual funds based on
           the user's risk appetite and verified Sharpe ratios.
========================================================
"""
import os
import argparse
import pandas as pd

def get_recommendations(risk_appetite):
    # Standardize input
    risk = risk_appetite.strip().lower()
    
    # Load verified datasets
    scorecard_path = "data/processed/power_bi/fact_scorecard.csv"
    fund_path = "data/processed/power_bi/dim_fund.csv"
    
    if not os.path.exists(scorecard_path) or not os.path.exists(fund_path):
        return None, "Error: Missing Power BI-ready CSV files. Run scripts first."
        
    scorecard = pd.read_csv(scorecard_path)
    fund = pd.read_csv(fund_path)
    
    # Drop scheme_name from scorecard to prevent duplicate column suffix
    scorecard = scorecard.drop(columns=['scheme_name'], errors='ignore')
    
    # Merge
    df = pd.merge(scorecard, fund, on="amfi_code")
    
    # Map user risk appetite to dataset risk grades
    # Equity schemes = Very High risk
    # Debt schemes = Moderate risk
    # Note: No "Low" risk funds exist in the 6 schemes. Low risk requests default to debt.
    if risk == "low":
        filtered = df[df['risk_grade'].str.lower() == "moderate"].copy()
        message = "Note: No 'Low' risk schemes are present in the current portfolio. Displaying the lowest risk available assets (Moderate Debt schemes):"
    elif risk == "moderate":
        filtered = df[df['risk_grade'].str.lower() == "moderate"].copy()
        message = "Displaying Moderate risk schemes (Debt & Money Market):"
    elif risk == "high":
        filtered = df[df['risk_grade'].str.lower() == "very high"].copy()
        message = "Displaying High risk schemes (Equity Growth schemes):"
    else:
        return None, f"Error: Invalid risk appetite '{risk_appetite}'. Choose from: Low, Moderate, High."
        
    if filtered.empty:
        return filtered, "No schemes found matching the criteria."
        
    # Rank by Sharpe Ratio descending
    filtered = filtered.sort_values(by="sharpe_ratio", ascending=False).reset_index(drop=True)
    
    # Take top 3 recommended
    top_3 = filtered.head(3).copy()
    return top_3, message

def main():
    parser = argparse.ArgumentParser(description="Bluestock Mutual Fund Recommender Engine")
    parser.add_argument("--risk", type=str, help="Risk appetite (Low, Moderate, High)")
    args = parser.parse_args()
    
    print("="*60)
    print("  BLUESTOCK FUND RECOMMENDATION ENGINE")
    print("="*60)
    
    risk_input = args.risk
    if not risk_input:
        # Interactive mode
        print("Select your Risk Appetite:")
        print("  1. Low (Conservative / Capital Preservation)")
        print("  2. Moderate (Balanced / Debt Accrual)")
        print("  3. High (Aggressive / Equity Growth)")
        choice = input("Enter choice (1-3 or text): ").strip().lower()
        if choice in ["1", "low"]:
            risk_input = "low"
        elif choice in ["2", "moderate"]:
            risk_input = "moderate"
        elif choice in ["3", "high"]:
            risk_input = "high"
        else:
            risk_input = choice
            
    print(f"\nProcessing recommendations for Risk Appetite: {risk_input.upper()}...\n")
    recs, msg = get_recommendations(risk_input)
    
    if recs is None:
        print(msg)
        return
        
    print(msg)
    print("-" * 110)
    print(f"{'Rank':<5} | {'AMFI Code':<10} | {'Scheme Name':<50} | {'Risk':<10} | {'Sharpe':<10} | {'Score':<10}")
    print("-" * 110)
    for idx, row in recs.iterrows():
        name = row['scheme_name'].split("-")[0].strip()
        print(f"{idx+1:<5} | {row['amfi_code']:<10} | {name:<50} | {row['risk_grade']:<10} | {row['sharpe_ratio']:<10.4f} | {row['overall_scorecard_score']:<10.2f}")
    print("-" * 110)
    print("="*60)

if __name__ == "__main__":
    main()
