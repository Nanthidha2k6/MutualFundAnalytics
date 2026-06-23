# ================================================================
#  filters.py — Reusable filter / selector UI components
#  Mutual Fund Analytics | Frontend Components
# ================================================================

import streamlit as st
import pandas as pd
from datetime import date, timedelta


def fund_selector(df: pd.DataFrame, key: str = "fund_select") -> str:
    """
    Render a single-fund dropdown selector.

    Returns the selected scheme_name string.
    """
    funds = sorted(df["scheme_name"].unique().tolist())

    # Shorten long names for display
    display_map = {f: (f[:55] + "..." if len(f) > 55 else f) for f in funds}
    display_opts = list(display_map.values())
    reverse_map  = {v: k for k, v in display_map.items()}

    st.markdown(
        "<p style='font-size:0.78rem;font-weight:600;color:#64748b;"
        "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px'>"
        "Select Fund</p>",
        unsafe_allow_html=True,
    )
    selected_display = st.selectbox(
        label="fund_selector_hidden",
        options=display_opts,
        key=key,
        label_visibility="collapsed",
    )
    return reverse_map[selected_display]


def multi_fund_selector(df: pd.DataFrame,
                        key: str = "multi_fund_select",
                        default_count: int = 3) -> list[str]:
    """
    Render a multi-select fund picker.

    Returns list of selected scheme_name strings.
    """
    funds = sorted(df["scheme_name"].unique().tolist())
    defaults = funds[:default_count]

    st.markdown(
        "<p style='font-size:0.78rem;font-weight:600;color:#64748b;"
        "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px'>"
        "Compare Funds</p>",
        unsafe_allow_html=True,
    )
    selected = st.multiselect(
        label="multi_fund_hidden",
        options=funds,
        default=defaults,
        key=key,
        label_visibility="collapsed",
        format_func=lambda x: x[:55] + "..." if len(x) > 55 else x,
    )
    if not selected:
        st.warning("Please select at least one fund.")
        return defaults
    return selected


def date_range_filter(df: pd.DataFrame,
                      key_prefix: str = "date") -> tuple[date, date]:
    """
    Render a start/end date picker constrained to the dataset range.

    Returns (start_date, end_date) as date objects.
    """
    df_dates = pd.to_datetime(df["date"], errors="coerce").dropna()
    min_date = df_dates.min().date()
    max_date = df_dates.max().date()

    # Default: last 3 years
    default_start = max(min_date, max_date - timedelta(days=3 * 365))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            "<p style='font-size:0.78rem;font-weight:600;color:#64748b;"
            "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px'>"
            "From Date</p>",
            unsafe_allow_html=True,
        )
        start_date = st.date_input(
            label="start_date_hidden",
            value=default_start,
            min_value=min_date,
            max_value=max_date,
            key=f"{key_prefix}_start",
            label_visibility="collapsed",
        )

    with col2:
        st.markdown(
            "<p style='font-size:0.78rem;font-weight:600;color:#64748b;"
            "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px'>"
            "To Date</p>",
            unsafe_allow_html=True,
        )
        end_date = st.date_input(
            label="end_date_hidden",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key=f"{key_prefix}_end",
            label_visibility="collapsed",
        )

    if start_date > end_date:
        st.error("Start date must be before end date.")
        start_date = default_start

    return start_date, end_date


def period_quick_select(key: str = "period_qs") -> int:
    """
    Quick period selector buttons: 1M / 3M / 6M / 1Y / 3Y / All.
    Returns number of days for the selected period.
    """
    options = {
        "1M": 30,
        "3M": 90,
        "6M": 180,
        "1Y": 365,
        "3Y": 1095,
        "All": 99999,
    }

    st.markdown(
        "<p style='font-size:0.78rem;font-weight:600;color:#64748b;"
        "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px'>"
        "Quick Period</p>",
        unsafe_allow_html=True,
    )

    selected = st.radio(
        label="period_hidden",
        options=list(options.keys()),
        index=3,  # default: 1Y
        horizontal=True,
        key=key,
        label_visibility="collapsed",
    )
    return options[selected]


def rolling_window_selector(key: str = "roll_win") -> int:
    """
    Slider for rolling return window in days.
    Returns selected window (days).
    """
    st.markdown(
        "<p style='font-size:0.78rem;font-weight:600;color:#64748b;"
        "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px'>"
        "Rolling Window (days)</p>",
        unsafe_allow_html=True,
    )
    return st.slider(
        label="roll_window_hidden",
        min_value=7,
        max_value=365,
        value=30,
        step=7,
        key=key,
        label_visibility="collapsed",
    )


def filter_df_by_period(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """
    Filter a DataFrame to keep only the last N days of data.
    Assumes a 'date' column (string or datetime).
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if days >= 99999:
        return df
    cutoff = df["date"].max() - pd.Timedelta(days=days)
    return df[df["date"] >= cutoff].reset_index(drop=True)


def filter_df_by_dates(df: pd.DataFrame,
                       start: date, end: date) -> pd.DataFrame:
    """
    Filter DataFrame between start_date and end_date.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)
    return df[mask].reset_index(drop=True)
