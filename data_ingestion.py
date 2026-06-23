"""
========================================================
  Mutual Fund Analytics - Day 1: Data Ingestion
  File   : data_ingestion.py
  Author : Student Project
  Purpose: Load, explore, and validate all CSV datasets
           placed inside data/raw/
========================================================
"""

import os
import sys
import glob
import pandas as pd
from pathlib import Path

# Fix UnicodeEncodeError on Windows terminals using CP1252 encoding.
# Reconfiguring stdout to UTF-8 ensures all print() calls work correctly.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ──────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────

# Root of the project (same folder as this script)
PROJECT_ROOT = Path(__file__).resolve().parent

# Folder where raw CSVs live
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Separator line for pretty printing
SEP_LINE = "=" * 70
THIN_LINE = "-" * 70


# ──────────────────────────────────────────────────────────────
# HELPER UTILITIES
# ──────────────────────────────────────────────────────────────

def print_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{SEP_LINE}")
    print(f"  {title}")
    print(SEP_LINE)


def print_subheader(title: str) -> None:
    """Print a lighter sub-section header."""
    print(f"\n{THIN_LINE}")
    print(f"  {title}")
    print(THIN_LINE)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names:
      - strip leading/trailing whitespace
      - convert to lowercase
      - replace spaces with underscores
    This makes column lookups consistent regardless of source formatting.
    """
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df


# ──────────────────────────────────────────────────────────────
# SECTION A — LOAD ALL CSV FILES FROM data/raw/
# ──────────────────────────────────────────────────────────────

def load_all_csvs(raw_dir: Path) -> dict:
    """
    Detect and load every CSV file found in raw_dir.

    Returns a dictionary:
        { "fund_master.csv": <DataFrame>, "nav_history.csv": <DataFrame>, ... }
    """
    print_header("SECTION A — Loading CSV Datasets")

    # Guard: make sure the directory exists
    if not raw_dir.exists():
        print(f"[ERROR] Directory not found: {raw_dir}")
        print("        Please create 'data/raw/' and place your CSV files inside it.")
        return {}

    # Find all .csv files (case-insensitive on Windows, explicit on Linux)
    csv_files = sorted(raw_dir.glob("*.csv"))

    if not csv_files:
        print(f"[WARNING] No CSV files found in: {raw_dir}")
        print("          Place your dataset CSV files in 'data/raw/' and re-run.")
        return {}

    datasets = {}

    for csv_path in csv_files:
        file_name = csv_path.name  # e.g. "fund_master.csv"
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            df = normalize_columns(df)          # normalise column names
            datasets[file_name] = df
            print(f"  [OK] Loaded '{file_name}'  →  {df.shape[0]:,} rows × {df.shape[1]} columns")
        except Exception as exc:
            print(f"  [FAIL] Could not load '{file_name}': {exc}")

    print(f"\n  Total datasets loaded: {len(datasets)}")
    return datasets


# ──────────────────────────────────────────────────────────────
# SECTION B — BASIC EXPLORATION FOR EACH DATASET
# ──────────────────────────────────────────────────────────────

def explore_datasets(datasets: dict) -> None:
    """
    For every loaded dataset print:
      - Shape (rows × columns)
      - Column data-types
      - First 5 rows (head)
    """
    print_header("SECTION B — Dataset Exploration (Shape / Dtypes / Head)")

    for name, df in datasets.items():
        print_subheader(f"Dataset: {name}")

        print(f"\n  Shape   : {df.shape[0]:,} rows × {df.shape[1]} columns")

        print(f"\n  Column Data-Types:")
        for col, dtype in df.dtypes.items():
            print(f"    {col:<40} {str(dtype)}")

        print(f"\n  First 5 Rows:")
        # Temporarily widen pandas display for readability
        with pd.option_context("display.max_columns", None,
                               "display.width", 120,
                               "display.max_colwidth", 40):
            print(df.head().to_string(index=True))


# ──────────────────────────────────────────────────────────────
# SECTION C — ANOMALY DETECTION
# ──────────────────────────────────────────────────────────────

def detect_anomalies(datasets: dict) -> dict:
    """
    For each dataset, detect and report:
      1. Missing values per column
      2. Duplicate rows
      3. Object columns (may need encoding/cleaning)
      4. Column-name formatting issues (original names before normalisation)
      5. Completely empty rows

    Returns a summary dictionary used later in Section F.
    """
    print_header("SECTION C — Anomaly Detection")

    anomaly_summary = {}   # { file_name: { "has_missing": bool, "has_dupes": bool } }

    for name, df in datasets.items():
        print_subheader(f"Anomalies in: {name}")

        # ── 1. Missing Values ──────────────────────────────────
        missing = df.isnull().sum()
        missing = missing[missing > 0]  # keep only columns that have nulls
        total_missing = missing.sum()

        if total_missing == 0:
            print(f"  [+] Missing Values : None found")
        else:
            print(f"\n  [!] Missing Values : {total_missing:,} total null cells across {len(missing)} column(s)")
            for col, cnt in missing.items():
                pct = cnt / len(df) * 100
                print(f"      {col:<40} {cnt:>6,} nulls  ({pct:.1f}%)")

        # ── 2. Duplicate Rows ──────────────────────────────────
        dupe_count = df.duplicated().sum()
        if dupe_count == 0:
            print(f"  [+] Duplicate Rows : None found")
        else:
            print(f"\n  [!] Duplicate Rows : {dupe_count:,} duplicate row(s) detected")

        # ── 3. Object-dtype Columns ────────────────────────────
        obj_cols = df.select_dtypes(include="object").columns.tolist()
        if obj_cols:
            print(f"\n  [i] Object-dtype Columns (may need cleaning/encoding):")
            for col in obj_cols:
                n_unique = df[col].nunique()
                sample_vals = df[col].dropna().unique()[:3].tolist()
                print(f"      {col:<40} unique={n_unique:<6} sample={sample_vals}")
        else:
            print(f"  [+] No object-dtype columns found")

        # ── 4. Column Naming Issues ────────────────────────────
        # Re-read the raw CSV column names to check for whitespace/case issues
        raw_cols_path = RAW_DATA_DIR / name
        try:
            raw_df_cols = pd.read_csv(raw_cols_path, nrows=0).columns.tolist()
            bad_cols = [c for c in raw_df_cols
                        if c != c.strip() or any(ch.isupper() for ch in c) or "  " in c]
            if bad_cols:
                print(f"\n  [!] Column Naming Issues (raw names before normalisation):")
                for col in bad_cols:
                    print(f"      '{col}'")
            else:
                print(f"  [+] Column Names    : Clean (no extra spaces or mixed-case issues)")
        except Exception:
            pass  # skip if re-read fails

        # ── 5. Empty Rows ──────────────────────────────────────
        empty_rows = df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            print(f"\n  [!] Completely Empty Rows : {empty_rows}")
        else:
            print(f"  [+] Empty Rows      : None found")

        # Store summary flags
        anomaly_summary[name] = {
            "has_missing": total_missing > 0,
            "has_dupes":   dupe_count > 0,
            "missing_cols_count": len(missing),
            "dupe_count":  dupe_count,
        }

    return anomaly_summary


# ──────────────────────────────────────────────────────────────
# SECTION D — FUND_MASTER EXPLORATION
# ──────────────────────────────────────────────────────────────

def explore_fund_master(datasets: dict) -> None:
    """
    If fund_master.csv is loaded, print:
      - Unique fund houses
      - Unique categories
      - Unique sub-categories
      - Unique risk grades
    Column names are already normalised (lowercase, underscores).
    """
    print_header("SECTION D — Fund Master Deep-Dive")

    fm_key = next((k for k in datasets if "fund_master" in k.lower()), None)

    if fm_key is None:
        print("  [SKIP] 'fund_master.csv' not found in data/raw/.")
        print("         Place the file there and re-run to see this section.")
        return

    df = datasets[fm_key]

    # Map of human-readable label → possible normalised column name variants
    fields_to_explore = {
        "Fund Houses"    : ["fund_house", "amc", "amc_name", "fund_house_name"],
        "Categories"     : ["category", "fund_category", "scheme_category"],
        "Sub-Categories" : ["sub_category", "sub-category", "subcategory", "scheme_sub_category"],
        "Risk Grades"    : ["risk", "risk_grade", "risk_level", "riskometer"],
    }

    for label, candidate_cols in fields_to_explore.items():
        # Find which candidate column actually exists in this DataFrame
        matched_col = next((c for c in candidate_cols if c in df.columns), None)

        if matched_col is None:
            print(f"\n  [!] {label}: column not found. Tried: {candidate_cols}")
            continue

        unique_vals = sorted(df[matched_col].dropna().unique().tolist())
        print(f"\n  {label} ({len(unique_vals)} unique)  [column: '{matched_col}']")
        for val in unique_vals:
            print(f"      • {val}")


# ──────────────────────────────────────────────────────────────
# SECTION E — AMFI SCHEME CODE VALIDATION
# ──────────────────────────────────────────────────────────────

def validate_amfi_scheme_codes(datasets: dict) -> dict:
    """
    Cross-validate AMFI scheme codes between fund_master and nav_history.

    Returns a dict with validation results.
    """
    print_header("SECTION E — AMFI Scheme Code Validation")

    result = {
        "ran"          : False,
        "total_master" : 0,
        "total_nav"    : 0,
        "matched"      : 0,
        "missing"      : 0,
        "missing_list" : [],
    }

    # ── Locate fund_master ───────────────────────────────────
    fm_key = next((k for k in datasets if "fund_master" in k.lower()), None)
    nh_key = next((k for k in datasets if "nav_history" in k.lower() or "combined" in k.lower()), None)

    if fm_key is None:
        print("  [SKIP] 'fund_master.csv' not found — cannot run validation.")
        return result
    if nh_key is None:
        print("  [SKIP] 'nav_history.csv' or 'live_nav_combined.csv' not found — cannot run validation.")
        return result

    fm_df = datasets[fm_key]
    nh_df = datasets[nh_key]

    # ── Identify scheme-code column in each DataFrame ────────
    scheme_col_candidates = [
        "scheme_code", "amfi_code", "amfi_scheme_code",
        "code", "schemecode", "scheme_id",
    ]

    fm_code_col = next((c for c in scheme_col_candidates if c in fm_df.columns), None)
    nh_code_col = next((c for c in scheme_col_candidates if c in nh_df.columns), None)

    if fm_code_col is None:
        print(f"  [ERROR] Could not find scheme-code column in '{fm_key}'.")
        print(f"          Available columns: {list(fm_df.columns)}")
        return result
    if nh_code_col is None:
        print(f"  [ERROR] Could not find scheme-code column in '{nh_key}'.")
        print(f"          Available columns: {list(nh_df.columns)}")
        return result

    # ── Perform set comparison ───────────────────────────────
    master_codes = set(fm_df[fm_code_col].dropna().astype(str).str.strip())
    nav_codes    = set(nh_df[nh_code_col].dropna().astype(str).str.strip())
    matched      = master_codes & nav_codes
    missing      = master_codes - nav_codes

    result.update({
        "ran"          : True,
        "total_master" : len(master_codes),
        "total_nav"    : len(nav_codes),
        "matched"      : len(matched),
        "missing"      : len(missing),
        "missing_list" : sorted(list(missing)),
    })

    # ── Pretty-print results ─────────────────────────────────
    print(f"\n  Source file (fund_master) : '{fm_key}'  [column: '{fm_code_col}']")
    print(f"  Target file (nav_history) : '{nh_key}'  [column: '{nh_code_col}']")
    print(f"\n  Total scheme codes in fund_master : {len(master_codes):>6,}")
    print(f"  Unique scheme codes in nav_history: {len(nav_codes):>6,}")
    print(f"  Matched (present in both)         : {len(matched):>6,}")
    print(f"  Missing from nav_history          : {len(missing):>6,}")

    if missing:
        display_limit = 20
        show = sorted(list(missing))[:display_limit]
        print(f"\n  [!] First {min(len(missing), display_limit)} missing scheme codes:")
        for code in show:
            print(f"      {code}")
        if len(missing) > display_limit:
            print(f"      ... and {len(missing) - display_limit} more.")
    else:
        print("\n  [✓] All scheme codes in fund_master are present in nav_history.")

    return result


# ──────────────────────────────────────────────────────────────
# SECTION F — DATA QUALITY SUMMARY
# ──────────────────────────────────────────────────────────────

def print_data_quality_summary(datasets: dict,
                                anomaly_summary: dict,
                                amfi_result: dict) -> None:
    """
    Print a concise overall quality report covering all loaded files.
    """
    print_header("SECTION F — Data Quality Summary")

    total_files      = len(datasets)
    files_with_miss  = sum(1 for v in anomaly_summary.values() if v["has_missing"])
    files_with_dupes = sum(1 for v in anomaly_summary.values() if v["has_dupes"])

    print(f"\n  Total CSV files loaded       : {total_files}")
    print(f"  Files with missing values    : {files_with_miss}")
    print(f"  Files with duplicate rows    : {files_with_dupes}")

    print(f"\n  Per-file snapshot:")
    print(f"  {'File':<35} {'Rows':>8}  {'Cols':>5}  {'Nulls?':<8}  {'Dupes?'}")
    print(f"  {'-'*35} {'-'*8}  {'-'*5}  {'-'*8}  {'-'*6}")
    for name, df in datasets.items():
        anom = anomaly_summary.get(name, {})
        null_flag  = "YES" if anom.get("has_missing") else "no"
        dupe_flag  = "YES" if anom.get("has_dupes")   else "no"
        print(f"  {name:<35} {df.shape[0]:>8,}  {df.shape[1]:>5}  {null_flag:<8}  {dupe_flag}")

    print(f"\n  AMFI Scheme Code Validation:")
    if amfi_result["ran"]:
        status = "PASS ✓" if amfi_result["missing"] == 0 else "FAIL ✗"
        print(f"    Status          : {status}")
        print(f"    Matched codes   : {amfi_result['matched']:,}")
        print(f"    Missing codes   : {amfi_result['missing']:,}")
    else:
        print("    Status          : SKIPPED (fund_master or nav_history not found)")

    print(f"\n  Important Anomalies:")
    any_anomaly = False
    for name, anom in anomaly_summary.items():
        msgs = []
        if anom["has_missing"]:
            msgs.append(f"{anom['missing_cols_count']} column(s) have nulls")
        if anom["has_dupes"]:
            msgs.append(f"{anom['dupe_count']:,} duplicate rows")
        if msgs:
            any_anomaly = True
            print(f"    {name}: {', '.join(msgs)}")
    if not any_anomaly:
        print("    None — all datasets look clean!")

    print(f"\n{SEP_LINE}")
    print("  Day 1 Data Ingestion Complete. Review anomalies before Day 2.")
    print(SEP_LINE)


# ──────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(SEP_LINE)
    print("  MUTUAL FUND ANALYTICS - DAY 1: DATA INGESTION")
    print(f"  Raw data directory: {RAW_DATA_DIR}")
    print(SEP_LINE)

    # ── A: Load all CSVs ──────────────────────────────────────
    datasets = load_all_csvs(RAW_DATA_DIR)

    if not datasets:
        print("\n[ABORT] No datasets loaded. Nothing to process.")
        sys.exit(0)

    # ── B: Explore each dataset ───────────────────────────────
    explore_datasets(datasets)

    # ── C: Anomaly detection ──────────────────────────────────
    anomaly_summary = detect_anomalies(datasets)

    # ── D: Fund master deep-dive ──────────────────────────────
    explore_fund_master(datasets)

    # ── E: AMFI scheme code validation ───────────────────────
    amfi_result = validate_amfi_scheme_codes(datasets)

    # ── F: Overall data quality summary ──────────────────────
    print_data_quality_summary(datasets, anomaly_summary, amfi_result)
