# ================================================================
#  nav_comparison.py — Multi-Fund Comparison Page
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
    make_comparison_chart,
    make_returns_bar_chart,
    make_volatility_chart,
)
from frontend.components.metrics_cards import (
    page_header, section_header, divider, kpi_card,
)
from frontend.components.filters import (
    multi_fund_selector,
    period_quick_select,
    filter_df_by_period,
)


def build_returns_table(df: pd.DataFrame, funds: list[str]) -> pd.DataFrame:
    """
    Build a returns comparison DataFrame for the given funds.
    Computes 1M, 3M, 6M, 1Y, and total-period returns.
    """
    rows = []

    def period_return(fdf, days):
        cutoff = fdf["date"].max() - pd.Timedelta(days=days)
        sub    = fdf[fdf["date"] >= cutoff]
        if len(sub) < 2:
            return None
        return (sub["nav"].iloc[-1] / sub["nav"].iloc[0] - 1) * 100

    for fund in funds:
        fdf = df[df["scheme_name"] == fund].sort_values("date")
        if fdf.empty or len(fdf) < 2:
            continue

        total_ret = (fdf["nav"].iloc[-1] / fdf["nav"].iloc[0] - 1) * 100
        daily_ret = fdf["nav"].pct_change().dropna()
        vol       = daily_ret.std() * np.sqrt(252) * 100

        rows.append({
            "Fund"         : fund[:50],
            "Latest NAV"   : f"Rs. {fdf['nav'].iloc[-1]:.4f}",
            "1M Return"    : period_return(fdf, 30),
            "3M Return"    : period_return(fdf, 90),
            "6M Return"    : period_return(fdf, 180),
            "1Y Return"    : period_return(fdf, 365),
            "Total Return" : total_ret,
            "Volatility"   : vol,
        })

    return pd.DataFrame(rows)


def format_returns_table(df: pd.DataFrame) -> pd.DataFrame:
    """Format numeric return columns as percentage strings."""
    df = df.copy()
    for col in ["1M Return", "3M Return", "6M Return", "1Y Return", "Total Return"]:
        df[col] = df[col].apply(
            lambda x: f"{x:+.2f}%" if x is not None and not pd.isna(x) else "N/A"
        )
    df["Volatility"] = df["Volatility"].apply(lambda x: f"{x:.2f}%")
    return df


def show(df_all: pd.DataFrame, selected_days: int = 365) -> None:
    """Render the NAV Comparison page."""

    page_header(
        "NAV Comparison",
        "Compare multiple funds side-by-side — normalised performance, returns & risk"
    )

    # ── Selectors ─────────────────────────────────────────────────
    col_funds, col_period = st.columns([4, 2])
    with col_funds:
        selected_funds = multi_fund_selector(df_all, key="nc_funds", default_count=3)
    with col_period:
        days = period_quick_select(key="nc_period")

    # ── Filter data to selected funds and period ───────────────────
    df_sel = df_all[df_all["scheme_name"].isin(selected_funds)].copy()
    df_sel = filter_df_by_period(df_sel, days)

    if df_sel.empty:
        st.warning("No data available for the selected funds and period.")
        return

    divider()

    # ── KPI summary row ───────────────────────────────────────────
    section_header("📊", "Quick Comparison Snapshot")

    ret_table_raw = build_returns_table(df_sel, selected_funds)

    if not ret_table_raw.empty:
        cols = st.columns(len(selected_funds))
        for i, (_, row) in enumerate(ret_table_raw.iterrows()):
            with cols[i % len(cols)]:
                total = row["Total Return"]
                kpi_card(
                    label=row["Fund"][:28] + "...",
                    value=f"{total:+.1f}%",
                    icon="📈" if total >= 0 else "📉",
                    sub=row["Latest NAV"],
                    color="green" if total >= 0 else "red",
                    badge=f"{total:+.1f}%",
                    badge_up=(total >= 0),
                )

    divider()

    # ── Normalised Comparison Chart ───────────────────────────────
    section_header("📈", "Normalised Performance (Base = 100)")
    st.caption(
        "All funds are rebased to 100 at the start of the selected period for fair comparison."
    )
    fig_cmp = make_comparison_chart(df_sel, title=f"Comparison — Last {days} days")
    st.plotly_chart(fig_cmp, use_container_width=True, config={"displayModeBar": False})

    divider()

    # ── Returns Bar Chart ──────────────────────────────────────────
    section_header("📊", "Total Returns Comparison")

    if not ret_table_raw.empty:
        bar_df = ret_table_raw[["Fund", "Total Return"]].copy()
        bar_df = bar_df.rename(columns={"Fund": "scheme_name", "Total Return": "return_pct"})
        bar_df = bar_df.dropna(subset=["return_pct"])

        fig_bar = make_returns_bar_chart(bar_df)
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    divider()

    # ── Risk vs Return Scatter ─────────────────────────────────────
    section_header("⚖️", "Risk vs Return Map")
    st.caption("Funds in the top-left quadrant are ideal: high return, low risk.")

    if not ret_table_raw.empty:
        scatter_df = ret_table_raw[["Fund", "Total Return", "Volatility"]].copy()
        scatter_df = scatter_df.rename(columns={
            "Fund"        : "scheme_name",
            "Total Return": "return_pct",
            "Volatility"  : "volatility",
        })
        scatter_df["return_pct"] = pd.to_numeric(scatter_df["return_pct"], errors="coerce")
        scatter_df["volatility"] = pd.to_numeric(scatter_df["volatility"], errors="coerce")
        scatter_df = scatter_df.dropna()

        fig_scatter = make_volatility_chart(scatter_df)
        st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

    divider()

    # ── Detailed Returns Table ─────────────────────────────────────
    section_header("📋", "Detailed Returns Table")

    if not ret_table_raw.empty:
        formatted = format_returns_table(ret_table_raw)
        st.dataframe(formatted, use_container_width=True, hide_index=True)

        # Download comparison table as CSV
        csv_bytes = formatted.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️  Download Comparison Table as CSV",
            data=csv_bytes,
            file_name="nav_comparison.csv",
            mime="text/csv",
            key="dl_comparison",
        )

    divider()

    # ── Head-to-Head Latest NAV prices ────────────────────────────
    with st.expander("🔎 Latest NAV Prices for Selected Funds"):
        latest_rows = []
        for fund in selected_funds:
            fdf = df_all[df_all["scheme_name"] == fund].sort_values("date")
            if fdf.empty:
                continue
            latest_rows.append({
                "Fund"       : fund,
                "Date"       : fdf["date"].iloc[-1].strftime("%d %b %Y"),
                "NAV (Rs.)"  : f"{fdf['nav'].iloc[-1]:.4f}",
                "Scheme Code": int(fdf["scheme_code"].iloc[-1]) if "scheme_code" in fdf.columns else "-",
            })
        if latest_rows:
            st.dataframe(pd.DataFrame(latest_rows), use_container_width=True, hide_index=True)
