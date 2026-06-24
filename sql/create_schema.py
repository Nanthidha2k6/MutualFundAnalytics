"""
========================================================
  Mutual Fund Analytics - Day 2: SQLite Schema Builder
  File   : sql/create_schema.py
  Author : Student Project
  Purpose: Read DDL from sql/schema.sql and initialize the
           star schema database using SQLAlchemy.
========================================================
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Fix UnicodeEncodeError on Windows terminals using CP1252 encoding.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Configuration
SQL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SQL_DIR.parent
DB_PATH = PROJECT_ROOT / "bluestock_mf.db"
SCHEMA_SQL_PATH = SQL_DIR / "schema.sql"

def create_schema():
    print("="*60)
    print("  INITIALIZING DATABASE SCHEMA")
    print("="*60)
    print(f"Database File: {DB_PATH.resolve()}")
    print(f"Schema DDL   : {SCHEMA_SQL_PATH.resolve()}")
    
    if not SCHEMA_SQL_PATH.exists():
        print(f"[ERROR] Schema SQL file not found at: {SCHEMA_SQL_PATH}")
        sys.exit(1)
        
    # Read the SQL schema file
    with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
        sql_content = f.read()
        
    # Initialize SQLAlchemy database engine
    db_uri = f"sqlite:///{DB_PATH.resolve()}"
    print(f"SQLAlchemy Connection URI: {db_uri}")
    
    try:
        engine = create_engine(db_uri)
        
        # Split DDL into individual statements to execute them one by one
        statements = []
        current_stmt = []
        for line in sql_content.splitlines():
            trimmed = line.strip()
            if trimmed.startswith("--") or not trimmed:
                continue
            current_stmt.append(line)
            if trimmed.endswith(";"):
                statements.append("\n".join(current_stmt))
                current_stmt = []
                
        # Connect and execute schema creation statements within a single transaction block
        with engine.begin() as conn:
            # Enable foreign keys
            conn.execute(text("PRAGMA foreign_keys = ON;"))
            print("  [OK] Enabled PRAGMA foreign_keys = ON")
            
            for stmt in statements:
                stmt_text = stmt.strip()
                if not stmt_text:
                    continue
                # Extract statement header for logging
                header = stmt_text.split("\n")[0][:60]
                conn.execute(text(stmt_text))
                print(f"  [OK] Executed statement: {header}...")
                
        print("\n[SUCCESS] SQLite star schema database initialized successfully.")
        
    except Exception as exc:
        print(f"\n[FAIL] Error occurred while creating schema: {exc}")
        sys.exit(1)
    print("="*60)

if __name__ == "__main__":
    create_schema()
