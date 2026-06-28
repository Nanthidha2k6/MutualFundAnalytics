# ================================================================
#  performance_scorecard.py — Day 3 Scorecard Page
#  Mutual Fund Analytics | Dashboard Pages
# ================================================================

import sys
from pathlib import Path
import sqlite3
import streamlit as st
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from frontend.components.metrics_cards import (
    page_header, section_header, divider, kpi_card
)

def show(df_all: pd.DataFrame, selected_days: int = 365) -> None:
    page_header(
        "Performance Scorecard & Risk Metrics",
        "Day 3 Performance scorecard, risk metrics, and benchmark regression analysis (Strict Real Data)"
    )
    
    # Load from SQLite database or CSV as fallback
    db_path = ROOT / "data" / "processed" / "mutual_funds.db"
    scorecard_path = ROOT / "data" / "processed" / "fund_scorecard.csv"
    alpha_beta_path = ROOT / "data" / "processed" / "alpha_beta.csv"
    
    try:
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            # Verify table exists
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            if "fund_scorecard" in tables and "alpha_beta" in tables:
                scorecard_df = pd.read_sql("SELECT * FROM fund_scorecard", conn)
                ab_df = pd.read_sql("SELECT * FROM alpha_beta", conn)
            else:
                scorecard_df = pd.read_csv(scorecard_path)
                ab_df = pd.read_csv(alpha_beta_path)
            conn.close()
        else:
            scorecard_df = pd.read_csv(scorecard_path)
            ab_df = pd.read_csv(alpha_beta_path)
    except Exception as exc:
        st.error(f"Failed to load Day 3 analytics data: {exc}")
        return

    # Check if empty
    if scorecard_df.empty:
        st.warning("No scorecard data available. Run the verify_day3.py script first.")
        return
        
    # Sort scorecard by score descending
    scorecard_df = scorecard_df.sort_values("overall_scorecard_score", ascending=False).reset_index(drop=True)
    
    # ── KPIs Row ──────────────────────────────────────────────────
    section_header("🏆", "Scorecard Leaderboard")
    c1, c2, c3 = st.columns(3)
    
    leader = scorecard_df.iloc[0]
    second = scorecard_df.iloc[1]
    least_cost = scorecard_df.sort_values("expense_ratio_percent").iloc[0]
    
    with c1:
        kpi_card(
            "Overall Leader", f"{leader['overall_scorecard_score']:.1f} pts",
            "🥇", leader["scheme_name"].split('-')[0].strip(), "green"
        )
    with c2:
        kpi_card(
            "Runner Up", f"{second['overall_scorecard_score']:.1f} pts",
            "🥈", second["scheme_name"].split('-')[0].strip(), "blue"
        )
    with c3:
        kpi_card(
            "Lowest Cost Fund", f"{least_cost['expense_ratio_percent']:.2f}%",
            "💎", least_cost["scheme_name"].split('-')[0].strip(), "teal"
        )
        
    divider()
    
    # ── Data Table ────────────────────────────────────────────────
    section_header("📋", "Calculated Performance & Risk Metrics")
    
    # Format columns for display
    display_df = scorecard_df.copy()
    display_df["3Y CAGR (%)"] = (display_df["cagr_3y"] * 100).map(lambda x: f"{x:+.2f}%" if not pd.isna(x) else "N/A")
    display_df["Sharpe Ratio"] = display_df["sharpe_ratio"].map(lambda x: f"{x:.4f}" if not pd.isna(x) else "N/A")
    display_df["Sortino Ratio"] = display_df["sortino_ratio"].map(lambda x: f"{x:.4f}" if not pd.isna(x) else "N/A")
    display_df["Max Drawdown (%)"] = (display_df["max_drawdown"] * 100).map(lambda x: f"{x:.2f}%" if not pd.isna(x) else "N/A")
    display_df["Expense Ratio (%)"] = display_df["expense_ratio_percent"].map(lambda x: f"{x:.2f}%" if not pd.isna(x) else "N/A")
    display_df["Score"] = display_df["overall_scorecard_score"]
    
    # Merge Alpha/Beta for display
    display_df = pd.merge(display_df, ab_df, on="amfi_code", how="left")
    display_df["Beta"] = display_df["beta"].map(lambda x: f"{x:.4f}" if not pd.isna(x) else "N/A")
    display_df["Annual Alpha (%)"] = (display_df["alpha_annualized"] * 100).map(lambda x: f"{x:+.2f}%" if not pd.isna(x) else "N/A")
    display_df["Tracking Error (%)"] = (display_df["tracking_error_annualized"] * 100).map(lambda x: f"{x:.2f}%" if not pd.isna(x) else "N/A")
    
    display_cols = [
        "scheme_name", "3Y CAGR (%)", "Sharpe Ratio", "Sortino Ratio", 
        "Max Drawdown (%)", "Expense Ratio (%)", "Beta", "Annual Alpha (%)", "Tracking Error (%)", "Score"
    ]
    
    st.dataframe(
        display_df[display_cols].rename(columns={"scheme_name": "Mutual Fund Scheme"}),
        use_container_width=True,
        hide_index=True
    )
    
    divider()
    
    # ── Visualizations ────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Overall Scorecard Comparison & Growth Chart</div>', unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns([5, 5])
    
    with col_chart1:
        # Plotly Bar Chart of Overall Score
        import plotly.express as px
        short_names = [n.split('-')[0].strip() for n in scorecard_df["scheme_name"]]
        fig = px.bar(
            scorecard_df,
            x="overall_scorecard_score",
            y=short_names,
            orientation='h',
            title="Overall Score (0-100 Scale)",
            labels={"x": "Score", "y": "Mutual Fund"},
            color="overall_scorecard_score",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        
    with col_chart2:
        # Show static matplotlib chart generated in reports/
        chart_file = ROOT / "reports" / "benchmark_comparison.png"
        if chart_file.exists():
            st.image(str(chart_file), caption="Normalized Cumulative Growth Comparison", use_container_width=True)
        else:
            st.info("Run verify_day3.py script to generate the growth chart.")
            
    divider()
    
    # ── Source Documentation ──────────────────────────────────────
    st.markdown("### 📚 Source Documentation & Notes")
    st.markdown("""
    - **Benchmark Data**: Fetched from Yahoo Finance Chart API (`v8/finance/chart`) for the period `2012-12-31` to `2026-06-19`.
      - Ticker `^NSEI` corresponds to the **Nifty 50 Index**.
      - Ticker `^CNX100` corresponds to the **Nifty 100 Index**.
    - **AUM & Expense Ratio**: Verified from official **ValueResearchOnline** fund profiles as of June 2026.
    - **Scorecard Weightages**: 3-Year CAGR (30%), Sharpe Ratio (25%), Sortino Ratio (20%), Max Drawdown (15%), and Expense Ratio (10%).
    - **Downside Volatility**: Calculated daily downside deviations below risk-free rate ($Rf_{daily} = 6.5\\% / 252$) to compute Sortino ratio.
    - **Tracking Error & Regression**: Aligned daily trading dates between indices and funds before running the regression.
    """)
