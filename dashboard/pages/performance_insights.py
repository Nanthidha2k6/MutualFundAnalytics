# ================================================================
#  performance_insights.py — Smart Auto-Insights Page
#  Mutual Fund Analytics | Dashboard Pages
# ================================================================

import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from frontend.components.metrics_cards import (
    page_header, section_header, divider,
    insight_card, kpi_card, stat_row,
)
from frontend.components.charts import make_returns_bar_chart, make_volatility_chart
from frontend.components.filters import filter_df_by_period, period_quick_select


# ── Analytics engine ─────────────────────────────────────────────

def _safe_vol(daily_ret: pd.Series) -> float:
    """
    Compute annualised volatility with NaN/outlier protection.
    Winsorises extreme daily returns (>50%) before computing std
    to avoid money-market or bond funds distorting the metric.
    """
    if daily_ret.empty:
        return np.nan
    # Remove extreme outliers: clip daily returns to [-50%, +50%]
    clipped = daily_ret.clip(-0.50, 0.50)
    std = clipped.std()
    if pd.isna(std) or std == 0:
        return np.nan
    return std * np.sqrt(252) * 100


def _safe_sharpe(daily_ret: pd.Series, rf_annual: float = 0.065) -> float:
    """
    Compute Sharpe ratio safely — returns 0 if std is 0 or NaN.
    Uses clipped returns consistent with _safe_vol.
    """
    if daily_ret.empty:
        return 0.0
    clipped = daily_ret.clip(-0.50, 0.50)
    rf_daily = rf_annual / 252
    excess   = clipped - rf_daily
    std      = clipped.std()
    if pd.isna(std) or std == 0:
        return 0.0
    sharpe = excess.mean() / std * np.sqrt(252)
    # Clamp to reasonable range to prevent display breakage
    return float(np.clip(sharpe, -10, 10))


def compute_all_fund_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute comprehensive metrics for ALL funds in the dataset.
    Returns one row per fund.
    NaN-safe: all division-by-zero and outlier cases are handled.
    """
    records = []

    for fund in df["scheme_name"].unique():
        fdf = df[df["scheme_name"] == fund].sort_values("date").copy()
        if len(fdf) < 20:
            continue

        navs       = fdf["nav"].astype(float)
        daily_ret  = navs.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
        latest_nav = navs.iloc[-1]

        # Total return
        total_ret = (navs.iloc[-1] / navs.iloc[0] - 1) * 100 if navs.iloc[0] != 0 else np.nan

        # Volatility (outlier-safe)
        ann_vol = _safe_vol(daily_ret)

        # Sharpe (outlier-safe)
        sharpe = _safe_sharpe(daily_ret)

        # Max drawdown
        roll_max = navs.expanding().max()
        drawdown = ((navs - roll_max) / roll_max * 100)
        max_dd   = drawdown.min()

        # Consistency: % of months with positive return
        fdf2 = fdf.copy()
        fdf2["month"] = fdf2["date"].dt.to_period("M")
        monthly     = fdf2.groupby("month")["nav"].last().pct_change().dropna()
        consistency = (monthly > 0).mean() * 100 if len(monthly) > 0 else 0

        # CAGR
        years = (fdf["date"].max() - fdf["date"].min()).days / 365
        cagr  = ((navs.iloc[-1] / navs.iloc[0]) ** (1 / years) - 1) * 100 \
                if (years > 0 and navs.iloc[0] != 0) else np.nan

        # Risk classification (NaN-safe)
        if pd.isna(ann_vol):
            risk = "Unknown"
        elif ann_vol < 10:
            risk = "Low"
        elif ann_vol < 20:
            risk = "Medium"
        else:
            risk = "High"

        records.append({
            "scheme_name"   : fund,
            "latest_nav"    : latest_nav,
            "total_return"  : total_ret,
            "cagr"          : cagr,
            "ann_vol"       : ann_vol,
            "sharpe"        : sharpe,
            "max_drawdown"  : max_dd,
            "consistency"   : consistency,
            "risk"          : risk,
            "data_points"   : len(fdf),
        })

    return pd.DataFrame(records)


def get_insights(metrics_df: pd.DataFrame) -> dict:
    """
    Derive smart auto-insights from computed metrics.
    Returns a dictionary of insight labels → fund name / value.
    """
    if metrics_df.empty:
        return {}

    best_return   = metrics_df.loc[metrics_df["total_return"].idxmax()]
    worst_return  = metrics_df.loc[metrics_df["total_return"].idxmin()]
    most_stable   = metrics_df.loc[metrics_df["ann_vol"].idxmin()]
    most_volatile = metrics_df.loc[metrics_df["ann_vol"].idxmax()]
    best_sharpe   = metrics_df.loc[metrics_df["sharpe"].idxmax()]
    best_cagr     = metrics_df.loc[metrics_df["cagr"].idxmax()]
    most_consist  = metrics_df.loc[metrics_df["consistency"].idxmax()]
    least_dd      = metrics_df.loc[metrics_df["max_drawdown"].idxmax()]  # closest to 0

    return {
        "best_return"   : best_return,
        "worst_return"  : worst_return,
        "most_stable"   : most_stable,
        "most_volatile" : most_volatile,
        "best_sharpe"   : best_sharpe,
        "best_cagr"     : best_cagr,
        "most_consist"  : most_consist,
        "least_dd"      : least_dd,
    }


def show(df_all: pd.DataFrame, selected_days: int = 365) -> None:
    """Render the Performance Insights page."""

    page_header(
        "Performance Insights",
        "AI-generated analytics — best performers, risk leaders & smart comparisons"
    )

    # ── Period selector ───────────────────────────────────────────
    col_p, _ = st.columns([2, 6])
    with col_p:
        days = period_quick_select(key="pi_period")

    df_f = filter_df_by_period(df_all, days)
    metrics = compute_all_fund_metrics(df_f)

    if metrics.empty:
        st.warning("Not enough data to compute insights.")
        return

    insights = get_insights(metrics)

    divider()

    # ── Top KPI Row ───────────────────────────────────────────────
    section_header("🏆", "Performance Champions")

    c1, c2, c3, c4 = st.columns(4)

    best = insights["best_return"]
    worst = insights["worst_return"]
    stable = insights["most_stable"]
    sharpe = insights["best_sharpe"]

    with c1:
        kpi_card(
            "Best Return", f"{best['total_return']:+.1f}%",
            "🥇", best["scheme_name"][:28] + "...", "green",
            badge=f"{best['total_return']:+.1f}%", badge_up=True
        )
    with c2:
        kpi_card(
            "Lowest Return", f"{worst['total_return']:+.1f}%",
            "📉", worst["scheme_name"][:28] + "...", "red",
            badge=f"{worst['total_return']:+.1f}%", badge_up=(worst["total_return"] >= 0)
        )
    with c3:
        kpi_card(
            "Most Stable", f"{stable['ann_vol']:.1f}% vol",
            "🛡️", stable["scheme_name"][:28] + "...", "teal"
        )
    with c4:
        kpi_card(
            "Best Sharpe", f"{sharpe['sharpe']:.2f}",
            "⚡", sharpe["scheme_name"][:28] + "...", "purple"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    divider()

    # ── Auto-Insight Cards ────────────────────────────────────────
    section_header("💡", "Smart Insights")

    col_a, col_b = st.columns(2)

    with col_a:
        insight_card(
            "BEST PERFORMER",
            best["scheme_name"][:55],
            f"Total return: {best['total_return']:+.2f}% | "
            f"CAGR: {best['cagr']:.2f}%",
            color="green",
        )
        insight_card(
            "MOST CONSISTENT",
            insights["most_consist"]["scheme_name"][:55],
            f"Positive months: {insights['most_consist']['consistency']:.1f}% of all months",
            color="blue",
        )
        insight_card(
            "HIGHEST VOLATILITY",
            insights["most_volatile"]["scheme_name"][:55],
            f"Annualised volatility: {insights['most_volatile']['ann_vol']:.2f}% — higher risk",
            color="red",
        )
        insight_card(
            "SMALLEST DRAWDOWN",
            insights["least_dd"]["scheme_name"][:55],
            f"Max drawdown: {insights['least_dd']['max_drawdown']:.2f}% — capital preservation",
            color="teal",
        )

    with col_b:
        insight_card(
            "LOWEST RETURN",
            worst["scheme_name"][:55],
            f"Total return: {worst['total_return']:+.2f}% | Review allocation",
            color="orange",
        )
        insight_card(
            "BEST RISK-ADJUSTED (SHARPE)",
            sharpe["scheme_name"][:55],
            f"Sharpe ratio: {sharpe['sharpe']:.2f} — best return per unit of risk",
            color="purple",
        )
        insight_card(
            "MOST STABLE",
            stable["scheme_name"][:55],
            f"Volatility: {stable['ann_vol']:.2f}% — lowest price swings",
            color="green",
        )
        insight_card(
            "BEST CAGR",
            insights["best_cagr"]["scheme_name"][:55],
            f"CAGR: {insights['best_cagr']['cagr']:.2f}% per year",
            color="blue",
        )

    divider()

    # ── Full Metrics Table ─────────────────────────────────────────
    section_header("📋", "Complete Fund Scorecard")

    display_df = metrics.copy()
    display_df["Fund"] = display_df["scheme_name"].apply(lambda x: x[:50])
    display_df["Latest NAV"]   = display_df["latest_nav"].apply(
        lambda x: f"Rs. {x:.4f}" if pd.notna(x) else "N/A")
    display_df["Total Return"] = display_df["total_return"].apply(
        lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A")
    display_df["CAGR"]         = display_df["cagr"].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
    display_df["Volatility"]   = display_df["ann_vol"].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
    display_df["Sharpe Ratio"] = display_df["sharpe"].apply(
        lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    display_df["Max Drawdown"] = display_df["max_drawdown"].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
    display_df["Consistency"]  = display_df["consistency"].apply(
        lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    display_df["Risk Level"]   = display_df["risk"]

    show_cols = [
        "Fund", "Latest NAV", "Total Return", "CAGR",
        "Volatility", "Sharpe Ratio", "Max Drawdown",
        "Consistency", "Risk Level",
    ]
    final_table = display_df[show_cols].sort_values("Total Return", ascending=False)
    st.dataframe(final_table, use_container_width=True, hide_index=True)

    # ── Download Button ────────────────────────────────────────────
    csv_bytes = final_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download Scorecard as CSV",
        data=csv_bytes,
        file_name="fund_scorecard.csv",
        mime="text/csv",
        key="dl_scorecard",
    )

    divider()

    # ── Returns Bar Chart ──────────────────────────────────────────
    section_header("📊", "Total Returns — All Funds")

    bar_df = metrics[["scheme_name", "total_return"]].rename(
        columns={"total_return": "return_pct"}
    )
    fig_bar = make_returns_bar_chart(bar_df)
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    divider()

    # ── Risk vs Return Scatter ─────────────────────────────────────
    section_header("⚖️", "Risk vs Return Map — All Funds")

    scatter_df = metrics[["scheme_name", "total_return", "ann_vol"]].rename(
        columns={"total_return": "return_pct", "ann_vol": "volatility"}
    ).dropna(subset=["return_pct", "volatility"])   # drop NaN rows before plotting
    # Cap extreme volatility values so the scatter stays readable
    scatter_df["volatility"] = scatter_df["volatility"].clip(upper=100)
    if not scatter_df.empty:
        fig_scatter = make_volatility_chart(scatter_df)
        st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Not enough valid data to plot the risk-return map.")

    divider()

    # ── Interpretation guide ──────────────────────────────────────
    with st.expander("📖 How to Read These Metrics"):
        st.markdown("""
        | Metric | What it means |
        |--------|---------------|
        | **Total Return** | % gain/loss from start to end of selected period |
        | **CAGR** | Compound Annual Growth Rate — annualised return |
        | **Volatility** | Annualised std dev of daily returns — higher = riskier |
        | **Sharpe Ratio** | Return per unit of risk (>1 = good, >2 = excellent) |
        | **Max Drawdown** | Largest peak-to-trough fall — capital at risk |
        | **Consistency** | % of months with positive returns |
        | **Risk Level** | Low (<10% vol), Medium (10-20%), High (>20%) |
        """)
