# ================================================================
#  fund_analysis.py — Single Fund Deep-Dive Page
#  Mutual Fund Analytics | Dashboard Pages
# ================================================================

import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from frontend.components.charts import (
    make_nav_trend_chart,
    make_rolling_return_chart,
)
from frontend.components.metrics_cards import (
    page_header, section_header, divider,
    insight_card, fund_info_card, stat_row,
)
from frontend.components.filters import (
    fund_selector,
    period_quick_select,
    filter_df_by_period,
    rolling_window_selector,
)


def _safe_vol(daily_ret: pd.Series) -> float:
    """Volatility with outlier-clipping — handles money market / bond funds."""
    if daily_ret.empty:
        return np.nan
    clipped = daily_ret.clip(-0.50, 0.50)
    std = clipped.std()
    return float(std * np.sqrt(252) * 100) if (pd.notna(std) and std > 0) else np.nan


def _safe_sharpe(daily_ret: pd.Series, rf_annual: float = 0.065) -> float:
    """Sharpe ratio with outlier-clipping and division-by-zero guard."""
    if daily_ret.empty:
        return 0.0
    clipped  = daily_ret.clip(-0.50, 0.50)
    rf_daily = rf_annual / 252
    excess   = clipped - rf_daily
    std      = clipped.std()
    if pd.isna(std) or std == 0:
        return 0.0
    return float(np.clip(excess.mean() / std * np.sqrt(252), -10, 10))


def compute_fund_stats(df: pd.DataFrame) -> dict:
    """Compute key statistics for a single fund's NAV series."""
    df = df.sort_values("date").copy()
    navs = df["nav"].astype(float)

    if len(navs) < 2:
        return {}

    daily_returns = navs.pct_change().replace([np.inf, -np.inf], np.nan).dropna()

    total_ret  = (navs.iloc[-1] / navs.iloc[0] - 1) * 100 if navs.iloc[0] != 0 else np.nan
    ann_vol    = _safe_vol(daily_returns)
    max_nav    = navs.max()
    min_nav    = navs.min()
    latest_nav = navs.iloc[-1]
    oldest_nav = navs.iloc[0]
    sharpe     = _safe_sharpe(daily_returns)

    # Max drawdown
    rolling_max = navs.expanding().max()
    drawdown    = ((navs - rolling_max) / rolling_max) * 100
    max_dd      = drawdown.min()

    # 1M, 3M, 6M, 1Y returns
    def period_return(days):
        cutoff = df["date"].max() - pd.Timedelta(days=days)
        sub = df[df["date"] >= cutoff]
        if len(sub) < 2 or sub["nav"].iloc[0] == 0:
            return None
        return (sub["nav"].iloc[-1] / sub["nav"].iloc[0] - 1) * 100

    # Risk classification (NaN-safe)
    if pd.isna(ann_vol):
        risk = "Unknown"
    elif ann_vol < 10:
        risk = "Low"
    elif ann_vol < 20:
        risk = "Medium"
    else:
        risk = "High"

    return {
        "latest_nav" : latest_nav,
        "oldest_nav" : oldest_nav,
        "total_ret"  : total_ret,
        "ann_vol"    : ann_vol,
        "sharpe"     : sharpe,
        "max_dd"     : max_dd,
        "max_nav"    : max_nav,
        "min_nav"    : min_nav,
        "ret_1m"     : period_return(30),
        "ret_3m"     : period_return(90),
        "ret_6m"     : period_return(180),
        "ret_1y"     : period_return(365),
        "risk"       : risk,
        "records"    : len(df),
    }


def show(df_all: pd.DataFrame, selected_days: int = 365) -> None:
    """Render the Fund Analysis deep-dive page."""

    page_header(
        "Fund Analysis",
        "Deep-dive into a single mutual fund — NAV trend, returns & risk metrics"
    )

    # ── Controls Row ─────────────────────────────────────────────
    col_f, col_p, col_w = st.columns([3, 2, 2])
    with col_f:
        selected_fund = fund_selector(df_all, key="fa_fund")
    with col_p:
        days = period_quick_select(key="fa_period")
    with col_w:
        roll_win = rolling_window_selector(key="fa_roll")

    # ── Filter data ───────────────────────────────────────────────
    df_fund = df_all[df_all["scheme_name"] == selected_fund].copy()
    df_fund = filter_df_by_period(df_fund, days)

    if df_fund.empty:
        st.warning("No data available for the selected fund and period.")
        return

    stats = compute_fund_stats(df_fund)
    if not stats:
        st.warning("Insufficient data for analysis.")
        return

    divider()

    # ── Fund Info Card ────────────────────────────────────────────
    scheme_code = int(df_fund["scheme_code"].iloc[0]) if "scheme_code" in df_fund.columns else 0
    date_range  = (
        f"{df_fund['date'].min().strftime('%d %b %Y')} "
        f"to {df_fund['date'].max().strftime('%d %b %Y')}"
    )
    fund_info_card(
        scheme_name=selected_fund,
        scheme_code=scheme_code,
        date_range=date_range,
        total_records=stats["records"],
        risk_level=stats["risk"],
    )

    # ── Period Returns Stat Row ───────────────────────────────────
    def fmt_ret(v):
        if v is None:
            return "N/A"
        return f"{v:+.2f}%"

    stat_row([
        {"label": "1M Return",    "value": fmt_ret(stats["ret_1m"])},
        {"label": "3M Return",    "value": fmt_ret(stats["ret_3m"])},
        {"label": "6M Return",    "value": fmt_ret(stats["ret_6m"])},
        {"label": "1Y Return",    "value": fmt_ret(stats["ret_1y"])},
        {"label": "Total Return", "value": fmt_ret(stats["total_ret"])},
    ])

    # ── NAV Trend Chart ───────────────────────────────────────────
    section_header("📈", "NAV Price Trend")
    fig_trend = make_nav_trend_chart(df_fund, title=f"{selected_fund[:45]}... — NAV Trend")
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

    # ── Rolling Return Chart ──────────────────────────────────────
    section_header("🔄", f"{roll_win}-Day Rolling Return")
    fig_roll = make_rolling_return_chart(df_fund, window=roll_win)
    st.plotly_chart(fig_roll, use_container_width=True, config={"displayModeBar": False})

    divider()

    # ── Risk & Performance KPIs ───────────────────────────────────
    section_header("🧮", "Risk & Performance Metrics")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Latest NAV", f"Rs. {stats['latest_nav']:.4f}")
    with m2:
        vol_str = f"{stats['ann_vol']:.2f}%" if pd.notna(stats['ann_vol']) else "N/A"
        st.metric("Annualised Volatility", vol_str)
    with m3:
        st.metric("Sharpe Ratio", f"{stats['sharpe']:.2f}")
    with m4:
        st.metric("Max Drawdown", f"{stats['max_dd']:.2f}%")

    m5, m6, m7, m8 = st.columns(4)
    with m5:
        st.metric("All-time High NAV", f"Rs. {stats['max_nav']:.4f}")
    with m6:
        st.metric("All-time Low NAV",  f"Rs. {stats['min_nav']:.4f}")
    with m7:
        st.metric("First Recorded NAV", f"Rs. {stats['oldest_nav']:.4f}")
    with m8:
        st.metric("Total Return", f"{stats['total_ret']:+.2f}%")

    divider()

    # ── Auto Insights ─────────────────────────────────────────────
    section_header("💡", "Fund Insights")

    ic1, ic2 = st.columns(2)
    with ic1:
        risk_color = {"Low": "green", "Medium": "orange", "High": "red"}
        insight_card(
            "Risk Profile",
            f"{stats['risk']} Risk",
            f"Annualised volatility: {stats['ann_vol']:.2f}%",
            color=risk_color.get(stats["risk"], "blue"),
        )
        insight_card(
            "Sharpe Ratio",
            f"{stats['sharpe']:.2f}",
            "Risk-adjusted return (>1 is good, >2 is excellent)",
            color="purple" if stats["sharpe"] > 1 else "orange",
        )
    with ic2:
        insight_card(
            "Total Return",
            f"{stats['total_ret']:+.2f}%",
            f"Since {df_fund['date'].min().strftime('%d %b %Y')}",
            color="green" if stats["total_ret"] >= 0 else "red",
        )
        insight_card(
            "Max Drawdown",
            f"{stats['max_dd']:.2f}%",
            "Largest peak-to-trough decline in the period",
            color="red" if stats["max_dd"] < -20 else "orange",
        )

    divider()

    # ── Raw data preview + Download ───────────────────────────────
    with st.expander("📂 View Raw Data"):
        export_df = (
            df_fund[["date", "nav"]]
            .sort_values("date", ascending=False)
            .rename(columns={"date": "Date", "nav": "NAV (Rs.)"})
        )
        st.dataframe(export_df.head(100), use_container_width=True, hide_index=True)

        # Download full NAV history as CSV
        csv_bytes = export_df.to_csv(index=False).encode("utf-8")
        safe_name = selected_fund[:30].replace(" ", "_").replace("/", "-")
        st.download_button(
            label="⬇️  Download Full NAV History as CSV",
            data=csv_bytes,
            file_name=f"nav_{safe_name}.csv",
            mime="text/csv",
            key="dl_fund_nav",
        )
