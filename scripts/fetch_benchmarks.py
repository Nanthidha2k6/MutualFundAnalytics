"""
========================================================
  Mutual Fund Analytics - Day 3: Benchmark Data Ingestor
  File   : scripts/fetch_benchmarks.py
  Author : Student Project
  Purpose: Fetches daily closing prices for Nifty 50 and
           Nifty 100 from Yahoo Finance Chart API,
           computes daily returns, and saves to CSV.
========================================================
"""
import os
import requests
import pandas as pd
from datetime import datetime

def fetch_index_data(ticker, start_date="2012-12-31", end_date="2026-06-19"):
    # Convert dates to unix timestamps
    p1 = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    p2 = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={p1}&period2={p2}&interval=1d"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data for {ticker}: HTTP {response.status_code}")
        
    data = response.json()
    result = data.get("chart", {}).get("result", [])
    if not result:
        raise Exception(f"No result found in chart response for {ticker}")
        
    chart_data = result[0]
    timestamps = chart_data.get("timestamp", [])
    close_prices = chart_data.get("indicators", {}).get("quote", [{}])[0].get("close", [])
    
    if len(timestamps) != len(close_prices):
        raise Exception(f"Length mismatch between timestamps ({len(timestamps)}) and close prices ({len(close_prices)})")
        
    # Convert timestamps to dates (YYYY-MM-DD)
    dates = [datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d") for ts in timestamps]
    
    df = pd.DataFrame({
        "date": dates,
        f"{ticker}_close": close_prices
    })
    
    # Drop rows with null close prices
    df = df.dropna().reset_index(drop=True)
    
    # Calculate daily returns
    df[f"{ticker}_return"] = df[f"{ticker}_close"].pct_change()
    
    return df

def main():
    os.makedirs("data/processed", exist_ok=True)
    
    try:
        # Fetch Nifty 50
        nifty50_df = fetch_index_data("^NSEI")
        print(f"Fetched {len(nifty50_df)} records for Nifty 50.")
        
        # Fetch Nifty 100
        nifty100_df = fetch_index_data("^CNX100")
        print(f"Fetched {len(nifty100_df)} records for Nifty 100.")
        
        # Merge the two benchmarks
        merged_df = pd.merge(nifty50_df, nifty100_df, on="date", how="outer")
        merged_df = merged_df.sort_values("date").reset_index(drop=True)
        
        # Save to processed directory
        output_path = "data/processed/nifty_benchmarks_cleaned.csv"
        merged_df.to_csv(output_path, index=False)
        print(f"Successfully saved merged benchmarks to {output_path}")
        
    except Exception as e:
        print(f"Error during benchmark data fetch: {e}")
        exit(1)

if __name__ == "__main__":
    main()
