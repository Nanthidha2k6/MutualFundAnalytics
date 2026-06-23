import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

SQL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SQL_DIR.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "mutual_funds.db"

def get_connection():
    """Create and return a connection to the SQLite database with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_all_funds():
    """
    Fetch all funds from the database.
    Returns:
        pd.DataFrame: Columns are scheme_code, scheme_name, short_name, category, risk_grade.
    """
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM funds ORDER BY short_name;", conn)
    conn.close()
    return df

def get_nav_history(scheme_code=None):
    """
    Fetch daily NAV history.
    Args:
        scheme_code (int, optional): If provided, filters for that specific scheme.
    Returns:
        pd.DataFrame: Columns are scheme_code, date, nav.
    """
    conn = get_connection()
    if scheme_code:
        query = "SELECT scheme_code, date, nav FROM nav_history WHERE scheme_code = ? ORDER BY date;"
        df = pd.read_sql_query(query, conn, params=(int(scheme_code),))
    else:
        query = "SELECT scheme_code, date, nav FROM nav_history ORDER BY scheme_code, date;"
        df = pd.read_sql_query(query, conn)
    
    df["date"] = pd.to_datetime(df["date"])
    conn.close()
    return df

def get_nav_on_date(scheme_code, date_str):
    """
    Get the NAV for a scheme on a specific date. 
    If the date is a holiday/weekend, it returns the closest previous available trading day's NAV.
    Args:
        scheme_code (int): AMFI scheme code.
        date_str (str): Date in 'YYYY-MM-DD' format.
    Returns:
        tuple: (nav, actual_date_str) or (None, None)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Try to find the closest date on or before date_str
    cursor.execute("""
        SELECT nav, date FROM nav_history 
        WHERE scheme_code = ? AND date <= ? 
        ORDER BY date DESC LIMIT 1
    """, (int(scheme_code), date_str))
    
    row = cursor.fetchone()
    
    # If not found, try to find the closest date after date_str (fallback for early dates)
    if not row:
        cursor.execute("""
            SELECT nav, date FROM nav_history 
            WHERE scheme_code = ? AND date >= ? 
            ORDER BY date ASC LIMIT 1
        """, (int(scheme_code), date_str))
        row = cursor.fetchone()
        
    conn.close()
    if row:
        return float(row[0]), row[1]
    return None, None

def add_portfolio_transaction(scheme_code, purchase_date, amount):
    """
    Add a simulated transaction to the portfolio.
    Calculates units based on NAV on the purchase date.
    Args:
        scheme_code (int): AMFI scheme code.
        purchase_date (str): 'YYYY-MM-DD' format.
        amount (float): Amount invested in INR.
    Returns:
        dict: Summary of transaction inserted or error message.
    """
    nav, actual_date = get_nav_on_date(scheme_code, purchase_date)
    if nav is None:
        return {"success": False, "error": f"No NAV data available for scheme {scheme_code}."}
        
    units = amount / nav
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO portfolio_transactions (scheme_code, purchase_date, amount, units)
            VALUES (?, ?, ?, ?);
        """, (int(scheme_code), actual_date, float(amount), float(units)))
        conn.commit()
        tx_id = cursor.lastrowid
        success = True
        error = None
    except Exception as exc:
        conn.rollback()
        tx_id = None
        success = False
        error = str(exc)
    finally:
        conn.close()
        
    return {
        "success": success,
        "transaction_id": tx_id,
        "actual_date": actual_date,
        "nav": nav,
        "units": units,
        "error": error
    }

def get_portfolio_transactions():
    """
    Fetch all simulated portfolio transactions.
    Returns:
        pd.DataFrame: Columns include id, scheme_code, short_name, purchase_date, amount, units.
    """
    conn = get_connection()
    query = """
        SELECT t.id, t.scheme_code, f.short_name, f.scheme_name, t.purchase_date, t.amount, t.units
        FROM portfolio_transactions t
        JOIN funds f ON t.scheme_code = f.scheme_code
        ORDER BY t.purchase_date DESC;
    """
    df = pd.read_sql_query(query, conn)
    df["purchase_date"] = pd.to_datetime(df["purchase_date"])
    conn.close()
    return df

def delete_portfolio_transaction(transaction_id):
    """
    Delete a simulated transaction from the portfolio.
    Args:
        transaction_id (int): Transaction record ID.
    Returns:
        bool: True if successful, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM portfolio_transactions WHERE id = ?;", (int(transaction_id),))
        conn.commit()
        success = True
    except Exception:
        conn.rollback()
        success = False
    finally:
        conn.close()
    return success

def get_combined_nav_data_from_db():
    """
    Helper to fetch daily NAV history in format compatible with the existing dashboard:
    Columns: scheme_code, scheme_name, date, nav.
    Returns:
        pd.DataFrame
    """
    conn = get_connection()
    query = """
        SELECT n.scheme_code, f.scheme_name, n.date, n.nav
        FROM nav_history n
        JOIN funds f ON n.scheme_code = f.scheme_code
        ORDER BY f.scheme_name, n.date;
    """
    df = pd.read_sql_query(query, conn)
    df["date"] = pd.to_datetime(df["date"])
    conn.close()
    return df
