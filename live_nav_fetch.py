"""
========================================================
  Mutual Fund Analytics - Day 1: Live NAV Fetcher
  File   : live_nav_fetch.py
  Author : Student Project
  Purpose: Fetch live NAV data from MFAPI for selected
           mutual fund schemes and save as CSV files.
  API    : https://api.mfapi.in/mf/{scheme_code}
========================================================
"""

import os
import sys
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

# Fix UnicodeEncodeError on Windows terminals using CP1252 encoding.
# Reconfiguring stdout to UTF-8 ensures all print() calls work correctly.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ──────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────

# Root of the project
PROJECT_ROOT = Path(__file__).resolve().parent

# Folder where fetched CSVs will be saved
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# MFAPI base endpoint
MFAPI_BASE_URL = "https://api.mfapi.in/mf"

# Request timeout in seconds (avoid hanging forever)
REQUEST_TIMEOUT = 20

# Number of retries on timeout
REQUEST_RETRIES = 2

# Polite delay between requests (seconds) - avoids hammering the API
REQUEST_DELAY = 1.0

# ──────────────────────────────────────────────────────────────
# SCHEMES TO FETCH
# Each entry: (scheme_code, short_name_for_filename)
# ──────────────────────────────────────────────────────────────

SCHEMES = [
    (125497, "hdfc_top_100_direct"),
    (119551, "sbi_bluechip"),
    (120503, "icici_bluechip"),
    (118632, "nippon_large_cap"),
    (119092, "axis_bluechip"),
    (120841, "kotak_bluechip"),
]

# Separator for pretty printing
SEP_LINE  = "=" * 70
THIN_LINE = "-" * 70


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def print_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{SEP_LINE}")
    print(f"  {title}")
    print(SEP_LINE)


def ensure_raw_dir() -> None:
    """Create data/raw/ directory if it does not exist."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def build_output_filename(scheme_code: int, short_name: str) -> Path:
    """
    Build the output CSV path.
    Example: data/raw/nav_125497_hdfc_top_100_direct.csv
    """
    filename = f"nav_{scheme_code}_{short_name}.csv"
    return RAW_DATA_DIR / filename


# ──────────────────────────────────────────────────────────────
# FETCH A SINGLE SCHEME
# ──────────────────────────────────────────────────────────────

def fetch_scheme_nav(scheme_code: int, short_name: str) -> dict:
    """
    Fetch NAV history for a single scheme from MFAPI.

    Parameters
    ----------
    scheme_code : int   AMFI scheme code (e.g. 125497)
    short_name  : str   Short label used for the output filename

    Returns
    -------
    dict with keys:
        success      : bool
        scheme_code  : int
        scheme_name  : str   (from API metadata)
        df           : pd.DataFrame or None
        error        : str   (only when success=False)
    """
    url = f"{MFAPI_BASE_URL}/{scheme_code}"
    print(f"\n  Fetching scheme {scheme_code} ({short_name}) ...")
    print(f"  URL: {url}")

    # --- Send HTTP GET request (with retry on timeout) ---
    response = None
    last_error = None
    for attempt in range(1, REQUEST_RETRIES + 1):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()          # raises on 4xx / 5xx status
            break   # success — exit retry loop
        except requests.exceptions.ConnectionError as exc:
            return {
                "success": False, "scheme_code": scheme_code, "scheme_name": short_name,
                "df": None, "error": "Connection error - check your internet connection."
            }
        except requests.exceptions.Timeout:
            last_error = f"Request timed out after {REQUEST_TIMEOUT}s (attempt {attempt}/{REQUEST_RETRIES})."
            print(f"  [RETRY] {last_error}")
            time.sleep(2)   # brief pause before retrying
            continue
        except requests.exceptions.HTTPError as exc:
            return {
                "success": False, "scheme_code": scheme_code, "scheme_name": short_name,
                "df": None, "error": f"HTTP error: {exc}"
            }
    else:
        # All retries exhausted
        return {
            "success": False, "scheme_code": scheme_code, "scheme_name": short_name,
            "df": None, "error": last_error or "All retries failed."
        }

    # --- Parse JSON response ---
    try:
        data = response.json()
    except ValueError:
        return {
            "success": False, "scheme_code": scheme_code, "scheme_name": short_name,
            "df": None, "error": "Response is not valid JSON."
        }

    # --- Extract metadata ---
    meta = data.get("meta", {})
    scheme_name = (
        meta.get("scheme_name")
        or meta.get("fund_house")
        or f"Scheme {scheme_code}"
    )

    # --- Extract NAV history ---
    nav_data = data.get("data", [])
    if not nav_data:
        return {
            "success": False, "scheme_code": scheme_code, "scheme_name": scheme_name,
            "df": None, "error": "No NAV data returned by API."
        }

    # --- Convert to DataFrame ---
    try:
        df = pd.DataFrame(nav_data)          # columns: date, nav
        df["scheme_code"] = scheme_code
        df["scheme_name"] = scheme_name

        # Clean NAV: convert to float (API returns strings)
        df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

        # Parse date — MFAPI returns DD-MM-YYYY (e.g. "22-06-2026").
        # We try multiple formats for robustness in case the API changes.
        date_formats = ["%d-%m-%Y", "%d-%b-%Y", "%Y-%m-%d"]
        parsed = None
        for fmt in date_formats:
            try:
                parsed = pd.to_datetime(df["date"], format=fmt, errors="raise")
                # Check at least 80% of dates parsed successfully
                if parsed.notna().mean() >= 0.8:
                    break
            except Exception:
                parsed = None
        if parsed is None:
            # Last resort: let pandas infer the format
            parsed = pd.to_datetime(df["date"], infer_datetime_format=True, errors="coerce")
        df["date"] = parsed

        # Sort oldest to newest
        df.sort_values("date", inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Reorder columns for clarity
        df = df[["scheme_code", "scheme_name", "date", "nav"]]

    except Exception as exc:
        return {
            "success": False, "scheme_code": scheme_code, "scheme_name": scheme_name,
            "df": None, "error": f"DataFrame construction failed: {exc}"
        }

    return {
        "success": True,
        "scheme_code": scheme_code,
        "scheme_name": scheme_name,
        "df": df,
        "error": None,
    }


# ──────────────────────────────────────────────────────────────
# SAVE INDIVIDUAL SCHEME CSV
# ──────────────────────────────────────────────────────────────

def save_scheme_csv(result: dict, short_name: str) -> Path | None:
    """
    Save a single scheme's NAV DataFrame to CSV.

    Returns the output Path on success, None on failure.
    """
    if not result["success"] or result["df"] is None:
        return None

    out_path = build_output_filename(result["scheme_code"], short_name)
    try:
        result["df"].to_csv(out_path, index=False)
        return out_path
    except Exception as exc:
        print(f"  [ERROR] Could not write CSV: {exc}")
        return None


# ──────────────────────────────────────────────────────────────
# SAVE COMBINED CSV
# ──────────────────────────────────────────────────────────────

def save_combined_csv(all_results: list) -> Path | None:
    """
    Merge NAV history from all successfully fetched schemes
    into a single CSV: data/raw/live_nav_combined.csv

    Columns: scheme_code, scheme_name, date, nav
    """
    successful_dfs = [
        r["df"] for r in all_results
        if r["success"] and r["df"] is not None
    ]

    if not successful_dfs:
        print("\n  [WARNING] No successful fetches — combined CSV not created.")
        return None

    combined_df = pd.concat(successful_dfs, ignore_index=True)
    combined_df.sort_values(["scheme_code", "date"], inplace=True)
    combined_df.reset_index(drop=True, inplace=True)

    out_path = RAW_DATA_DIR / "live_nav_combined.csv"
    try:
        combined_df.to_csv(out_path, index=False)
        return out_path
    except Exception as exc:
        print(f"  [ERROR] Could not write combined CSV: {exc}")
        return None


# ──────────────────────────────────────────────────────────────
# PRINT STATUS LOG
# ──────────────────────────────────────────────────────────────

def print_status_log(all_results: list, out_paths: list) -> None:
    """
    Print a concise status table for all fetch operations.
    """
    print_header("FETCH STATUS SUMMARY")

    print(f"\n  {'Code':<8} {'Short Name':<30} {'Status':<10} {'Rows':>8}  Output File")
    print(f"  {'-'*8} {'-'*30} {'-'*10} {'-'*8}  {'-'*35}")

    for res, out_path in zip(all_results, out_paths):
        code      = str(res["scheme_code"])
        short     = str(res.get("short_name", ""))[:29]
        if res["success"]:
            status = "OK"
            rows   = f"{len(res['df']):,}"
            fname  = out_path.name if out_path else "-"
        else:
            status = "FAIL"
            rows   = "-"
            fname  = res["error"][:40] if res["error"] else "unknown error"

        print(f"  {code:<8} {short:<30} {status:<10} {rows:>8}  {fname}")

    successful = sum(1 for r in all_results if r["success"])
    print(f"\n  Fetched successfully : {successful} / {len(all_results)} schemes")


# ──────────────────────────────────────────────────────────────
# PRINT SCHEME METADATA
# ──────────────────────────────────────────────────────────────

def print_scheme_metadata(result: dict) -> None:
    """Print extracted metadata and a NAV preview for one scheme."""
    if not result["success"]:
        print(f"  [FAIL] {result['scheme_code']} - {result['error']}")
        return

    df = result["df"]
    print(f"  Scheme Name  : {result['scheme_name']}")
    print(f"  Scheme Code  : {result['scheme_code']}")
    print(f"  NAV Records  : {len(df):,}")
    if not df.empty:
        print(f"  Date Range   : {df['date'].min().date()}  to  {df['date'].max().date()}")
        print(f"  Latest NAV   : Rs. {df['nav'].iloc[-1]:.4f}")
        print(f"  Oldest NAV   : Rs. {df['nav'].iloc[0]:.4f}")
    print(f"\n  Preview (last 5 rows):")
    with pd.option_context("display.max_columns", None, "display.width", 100):
        print(df.tail(5).to_string(index=False))


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(SEP_LINE)
    print("  MUTUAL FUND ANALYTICS - DAY 1: LIVE NAV FETCH")
    print(f"  Run time  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Output dir: {RAW_DATA_DIR}")
    print(SEP_LINE)

    # Ensure output directory exists
    ensure_raw_dir()

    all_results = []   # collect results for all schemes
    out_paths   = []   # save paths (or None on failure)

    print_header("FETCHING NAV DATA FROM MFAPI")

    for scheme_code, short_name in SCHEMES:
        # --- Fetch ---
        result = fetch_scheme_nav(scheme_code, short_name)
        result["short_name"] = short_name    # store for later use

        # --- Print metadata ---
        print(f"\n  {'-'*60}")
        print_scheme_metadata(result)

        # --- Save individual CSV ---
        out_path = save_scheme_csv(result, short_name)
        if out_path:
            print(f"\n  [SAVED] {out_path.name}")
        else:
            print(f"\n  [NOT SAVED] Scheme {scheme_code} had errors.")

        all_results.append(result)
        out_paths.append(out_path)

        # Polite delay before the next request
        time.sleep(REQUEST_DELAY)

    # ── Save combined CSV ──────────────────────────────────────
    print_header("SAVING COMBINED NAV CSV")
    combined_path = save_combined_csv(all_results)
    if combined_path:
        combined_df = pd.read_csv(combined_path)
        print(f"  [SAVED] {combined_path.name}")
        print(f"  Total rows in combined file : {len(combined_df):,}")
        print(f"  Schemes included            : {combined_df['scheme_code'].nunique()}")
    else:
        print("  [SKIP] Combined CSV was not created.")

    # ── Final status log ───────────────────────────────────────
    print_status_log(all_results, out_paths)

    print(f"\n{SEP_LINE}")
    print("  Live NAV fetch complete. Check data/raw/ for output files.")
    print(SEP_LINE)
