"""
========================================================
  Bluestock Mutual Fund Analytics - Day 2 Orchestrator
  File   : day2_pipeline.py
  Author : Student Project
  Purpose: End-to-end orchestrator pipeline that runs
           cleaning, schema creation, data loading, and
           executes the 10 analytical queries.
========================================================
"""

import os
import sys
import subprocess
import sqlite3
import pandas as pd
from pathlib import Path

# Fix UnicodeEncodeError on Windows terminals using CP1252 encoding.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "bluestock_mf.db"
QUERIES_SQL_PATH = PROJECT_ROOT / "sql" / "queries.sql"

def run_step(script_path: str, description: str):
    print("\n" + "="*70)
    print(f"  STEP: {description}")
    print("="*70)
    
    cmd = [sys.executable, script_path]
    try:
        result = subprocess.run(cmd, check=True, text=True, cwd=str(PROJECT_ROOT))
        print(f"[SUCCESS] Step '{description}' completed successfully.")
    except subprocess.CalledProcessError as err:
        print(f"[ERROR] Step '{description}' failed with exit code {err.returncode}.")
        sys.exit(err.returncode)

def parse_queries_file(filepath: Path) -> list:
    """Parse sql/queries.sql into individual query blocks with their headers."""
    if not filepath.exists():
        print(f"[ERROR] Queries SQL file not found at: {filepath}")
        sys.exit(1)
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split queries by semicolon and clean them up
    queries = []
    current_comment = []
    
    for block in content.split(";"):
        block = block.strip()
        if not block:
            continue
            
        # Extract title or comments from the block
        comments = []
        sql_lines = []
        for line in block.splitlines():
            if line.strip().startswith("--"):
                comments.append(line.strip("-- ").strip())
            else:
                sql_lines.append(line)
                
        sql = "\n".join(sql_lines).strip()
        if not sql:
            continue
            
        # Deduce title from comments
        title = "Query"
        for c in comments:
            if "QUERY" in c.upper():
                title = c.strip()
                break
                
        queries.append({
            "title": title,
            "description": " | ".join(comments),
            "sql": sql + ";"
        })
        
    return queries

def execute_analytical_queries():
    print("\n" + "="*70)
    print("  STEP: EXECUTING 10 ANALYTICAL SQL QUERIES")
    print("="*70)
    
    queries = parse_queries_file(QUERIES_SQL_PATH)
    print(f"Parsed {len(queries)} query blocks from {QUERIES_SQL_PATH.name}.\n")
    
    if not DB_PATH.exists():
        print(f"[ERROR] Star schema database not found at {DB_PATH.resolve()}")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    
    # Enable foreign keys just in case
    conn.execute("PRAGMA foreign_keys = ON;")
    
    for idx, q in enumerate(queries, 1):
        print("-" * 70)
        print(f" {idx}. {q['title']}")
        print(f" Description: {q['description']}")
        print("-" * 70)
        
        try:
            df = pd.read_sql_query(q["sql"], conn)
            
            if df.empty:
                print("  [INFO] Query returned 0 rows.")
                # Print indicator if empty due to known missing data
                if any(tbl in q["sql"] for tbl in ["fact_transactions", "fact_performance", "fact_aum"]):
                    print("         * Note: This table is empty because source files")
                    print("           'investor_transactions.csv' or 'scheme_performance.csv'")
                    print("           were not present in the raw datasets.")
            else:
                # Widen display settings for pretty printing in console
                with pd.option_context("display.max_columns", None, 
                                       "display.width", 120, 
                                       "display.max_colwidth", 50):
                    print(df.to_string(index=False))
                    
        except Exception as exc:
            print(f"  [ERROR] Execution failed: {exc}")
            
        print()
        
    conn.close()
    print("="*70)
    print("  PIPELINE EXECUTION COMPLETE")
    print("="*70)

def main():
    print("="*80)
    print("  BLUESTOCK MUTUAL FUND ANALYTICS - DAY 2 PIPELINE")
    print("="*80)
    
    # 1. Clean Data
    run_step("scripts/clean_data.py", "Data Cleaning Pipeline")
    
    # 2. Create Star Schema
    run_step("sql/create_schema.py", "Schema DDL Initialization")
    
    # 3. Load Cleaned Data
    run_step("sql/load_cleaned_data.py", "Database Data Loader")
    
    # 4. Run Analytical Queries
    execute_analytical_queries()

if __name__ == "__main__":
    main()
