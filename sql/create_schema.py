import sqlite3
import os
from pathlib import Path

# Paths
SQL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SQL_DIR.parent
DB_DIR = PROJECT_ROOT / "data" / "processed"
DB_PATH = DB_DIR / "mutual_funds.db"

def create_schema():
    print(f"Creating SQLite database schema...")
    
    # Ensure processed directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # Connect to SQLite database (will create file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Create funds table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funds (
        scheme_code INTEGER PRIMARY KEY,
        scheme_name TEXT NOT NULL,
        short_name TEXT NOT NULL,
        category TEXT,
        risk_grade TEXT
    );
    """)
    
    # 2. Create nav_history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nav_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_code INTEGER NOT NULL,
        date TEXT NOT NULL,
        nav REAL NOT NULL,
        FOREIGN KEY (scheme_code) REFERENCES funds (scheme_code) ON DELETE CASCADE,
        UNIQUE(scheme_code, date)
    );
    """)
    
    # 3. Create portfolio_transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_code INTEGER NOT NULL,
        purchase_date TEXT NOT NULL,
        amount REAL NOT NULL,
        units REAL NOT NULL,
        FOREIGN KEY (scheme_code) REFERENCES funds (scheme_code) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()
    print(f"Database schema initialized successfully at: {DB_PATH}")

if __name__ == "__main__":
    create_schema()
