import sqlite3
import pandas as pd
from pathlib import Path

# Paths
SQL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SQL_DIR.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "mutual_funds.db"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
COMBINED_CSV = RAW_DIR / "live_nav_combined.csv"
MASTER_CSV = RAW_DIR / "fund_master.csv"

# Metadata mapping for the 6 funds we fetch
SCHEME_METADATA = {
    118632: {
        "fund_house": "Nippon India Mutual Fund",
        "category": "Equity",
        "sub_category": "Large Cap",
        "risk_grade": "Very High",
        "short_name": "Nippon India Large Cap"
    },
    119092: {
        "fund_house": "HDFC Mutual Fund",
        "category": "Debt",
        "sub_category": "Money Market",
        "risk_grade": "Moderate",
        "short_name": "HDFC Money Market"
    },
    119551: {
        "fund_house": "Aditya Birla Sun Life Mutual Fund",
        "category": "Debt",
        "sub_category": "Banking & PSU",
        "risk_grade": "Moderate",
        "short_name": "ABSL Banking & PSU"
    },
    120503: {
        "fund_house": "Axis Mutual Fund",
        "category": "Equity",
        "sub_category": "ELSS (Tax Saver)",
        "risk_grade": "Very High",
        "short_name": "Axis ELSS"
    },
    120841: {
        "fund_house": "Quant Mutual Fund",
        "category": "Equity",
        "sub_category": "Mid Cap",
        "risk_grade": "Very High",
        "short_name": "Quant Mid Cap"
    },
    125497: {
        "fund_house": "SBI Mutual Fund",
        "category": "Equity",
        "sub_category": "Small Cap",
        "risk_grade": "Very High",
        "short_name": "SBI Small Cap"
    }
}

def load_data():
    print("Starting data loading and fund master generation pipeline...")
    
    # 1. Guard: Check if live_nav_combined.csv exists
    if not COMBINED_CSV.exists():
        print(f"[ERROR] {COMBINED_CSV} not found! Please run live_nav_fetch.py first.")
        return
        
    df_nav = pd.read_csv(COMBINED_CSV)
    df_nav["date"] = pd.to_datetime(df_nav["date"]).dt.strftime("%Y-%m-%d")
    df_nav["nav"] = pd.to_numeric(df_nav["nav"], errors="coerce")
    df_nav = df_nav.dropna(subset=["date", "nav"])
    
    # 2. Generate and save fund_master.csv
    print("Generating fund_master.csv metadata...")
    master_rows = []
    for code in df_nav["scheme_code"].unique():
        code = int(code)
        # Find actual scheme name in combined data
        scheme_name = df_nav[df_nav["scheme_code"] == code]["scheme_name"].iloc[0]
        
        meta = SCHEME_METADATA.get(code, {
            "fund_house": "Unknown Mutual Fund",
            "category": "Unknown",
            "sub_category": "Unknown",
            "risk_grade": "Unknown",
            "short_name": f"Scheme {code}"
        })
        
        master_rows.append({
            "scheme_code": code,
            "scheme_name": scheme_name,
            "short_name": meta["short_name"],
            "fund_house": meta["fund_house"],
            "category": meta["category"],
            "sub_category": meta["sub_category"],
            "risk_grade": meta["risk_grade"]
        })
        
    df_master = pd.DataFrame(master_rows)
    df_master.to_csv(MASTER_CSV, index=False)
    print(f"fund_master.csv successfully generated and saved at: {MASTER_CSV}")
    
    # 3. Seed SQLite Database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Insert into funds table
    print("Seeding funds table...")
    funds_inserted = 0
    for _, row in df_master.iterrows():
        cursor.execute("""
        INSERT OR REPLACE INTO funds (scheme_code, scheme_name, short_name, category, risk_grade)
        VALUES (?, ?, ?, ?, ?);
        """, (int(row["scheme_code"]), row["scheme_name"], row["short_name"], 
              f"{row['category']}: {row['sub_category']}", row["risk_grade"]))
        funds_inserted += 1
        
    # Insert into nav_history table
    print("Seeding nav_history table (this may take a few seconds)...")
    nav_inserted = 0
    nav_skipped = 0
    
    # Prepare batch insert
    nav_records = []
    for _, row in df_nav.iterrows():
        nav_records.append((int(row["scheme_code"]), row["date"], float(row["nav"])))
        
    cursor.executemany("""
    INSERT OR IGNORE INTO nav_history (scheme_code, date, nav)
    VALUES (?, ?, ?);
    """, nav_records)
    
    conn.commit()
    
    # Get total inserted rows
    cursor.execute("SELECT COUNT(*) FROM funds;")
    total_funds = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM nav_history;")
    total_nav = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "="*50)
    print("  DATA LOADING PIPELINE SUMMARY")
    print("="*50)
    print(f"  Funds Loaded                : {total_funds}")
    print(f"  Daily NAV History Loaded     : {total_nav:,} rows")
    print(f"  Database File Location       : {DB_PATH}")
    print("="*50)
    print("Pipeline completed successfully.")

if __name__ == "__main__":
    load_data()
