import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import textwrap

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from sql.db_manager import (
    get_all_funds,
    add_portfolio_transaction,
    get_portfolio_transactions,
    delete_portfolio_transaction,
    get_nav_history,
)
from frontend.components.metrics_cards import page_header, divider, kpi_card, render_html

def show(df_all: pd.DataFrame, selected_days: int = 365) -> None:
    """Render the Portfolio Tracker dashboard page."""
    page_header(
        "Portfolio Tracker",
        "Simulate investments, view asset allocation, and track total portfolio returns"
    )
    
    # ── Database Status Guard ──────────────────────────────────────
    df_funds = get_all_funds()
    if df_funds.empty:
        st.warning("No fund details found in database. Run the seeding script first.")
        return
        
    # Get all transactions
    df_tx = get_portfolio_transactions()
    
    # Get latest NAV map for all funds
    nav_history = get_nav_history()
    if not nav_history.empty:
        latest_navs = nav_history.sort_values("date").groupby("scheme_code").last()
        latest_nav_map = latest_navs["nav"].to_dict()
        latest_date_map = latest_navs["date"].to_dict()
    else:
        latest_nav_map = {}
        latest_date_map = {}

    # ── Tabs layout: Overview & Manage Transactions ─────────────────
    tab_overview, tab_manage = st.tabs(["📊 Portfolio Dashboard", "➕ Manage Transactions"])
    
    with tab_manage:
        col_form, col_help = st.columns([2, 1])
        
        with col_form:
            st.markdown("### Add Simulated Purchase")
            with st.form("add_tx_form", clear_on_submit=True):
                fund_options = {row["scheme_name"]: row["scheme_code"] for _, row in df_funds.iterrows()}
                selected_fund_name = st.selectbox("Select Mutual Fund", list(fund_options.keys()))
                selected_code = fund_options[selected_fund_name]
                
                # Fetch min/max dates for this fund to guide the user
                fund_dates = nav_history[nav_history["scheme_code"] == selected_code]["date"]
                min_date = fund_dates.min().date() if not fund_dates.empty else datetime.date(2013, 1, 1)
                max_date = fund_dates.max().date() if not fund_dates.empty else datetime.date.today()
                
                purchase_date = st.date_input(
                    "Purchase Date", 
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date
                )
                
                amount = st.number_input(
                    "Amount Invested (INR)", 
                    min_value=500.0, 
                    value=10000.0, 
                    step=1000.0
                )
                
                submitted = st.form_submit_button("Add to Portfolio")
                
                if submitted:
                    res = add_portfolio_transaction(
                        selected_code, 
                        purchase_date.strftime("%Y-%m-%d"), 
                        amount
                    )
                    if res["success"]:
                        st.success(
                            f"Added successfully!\n\n"
                            f"Matched Date: **{res['actual_date']}** | "
                            f"NAV: **Rs. {res['nav']:.4f}** | "
                            f"Units: **{res['units']:.4f}**"
                        )
                        st.rerun()
                    else:
                        st.error(f"Error: {res['error']}")
                        
        with col_help:
            st.markdown("### Portfolio Instructions")
            st.info(
                "1. **Select a fund** and choose a purchase date in the past.\n"
                "2. **Enter amount** and click Submit.\n"
                "3. The system automatically fetches the NAV on your selected date. "
                "If it was a weekend/holiday, it will map to the closest previous trading day's NAV.\n"
                "4. View your simulated gains on the Dashboard tab!"
            )
            
    with tab_overview:
        if df_tx.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(
                "👋 **Your Portfolio is empty.** "
                "Click on the **'Manage Transactions'** tab to record your first simulated purchase!"
            )
            return
            
        # Calculate current values & returns
        df_tx["latest_nav"] = df_tx["scheme_code"].map(latest_nav_map)
        df_tx["current_value"] = df_tx["units"] * df_tx["latest_nav"]
        df_tx["profit_loss"] = df_tx["current_value"] - df_tx["amount"]
        df_tx["profit_loss_pct"] = (df_tx["profit_loss"] / df_tx["amount"]) * 100
        
        # Portfolio Totals
        total_invested = df_tx["amount"].sum()
        total_current = df_tx["current_value"].sum()
        total_pl = total_current - total_invested
        total_pl_pct = (total_pl / total_invested) * 100 if total_invested > 0 else 0.0
        
        # Display KPI cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi_card("Total Invested", f"₹{total_invested:,.2f}", "💼", "Total capital injected", "blue")
        with c2:
            kpi_card("Current Value", f"₹{total_current:,.2f}", "📈", "Valued at latest NAVs", "teal")
        with c3:
            badge_val = f"{total_pl_pct:+.2f}%"
            kpi_card(
                "Total Profit / Loss", 
                f"₹{total_pl:+,.2f}", 
                "🏆" if total_pl >= 0 else "📉", 
                "Net return", 
                "green" if total_pl >= 0 else "red",
                badge=badge_val,
                badge_up=(total_pl >= 0)
            )
        with c4:
            assets_count = df_tx["scheme_code"].nunique()
            kpi_card("Asset Count", str(assets_count), "📦", "Distinct mutual funds", "purple")
            
        divider()
        
        # ── Charts Row ─────────────────────────────────────────────
        st.markdown("### Portfolio Allocation & Growth")
        col_pie, col_bar = st.columns([1, 1])
        
        with col_pie:
            # Asset allocation by current value
            df_alloc = df_tx.groupby("short_name")["current_value"].sum().reset_index()
            fig_pie = px.pie(
                df_alloc, 
                values="current_value", 
                names="short_name",
                title="Current Asset Allocation (Weight %)",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_bar:
            # Performance by fund: Invested vs Current
            df_perf = df_tx.groupby("short_name")[["amount", "current_value"]].sum().reset_index()
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=df_perf["short_name"],
                y=df_perf["amount"],
                name="Invested Amount",
                marker_color="#3b82f6"
            ))
            fig_bar.add_trace(go.Bar(
                x=df_perf["short_name"],
                y=df_perf["current_value"],
                name="Current Value",
                marker_color="#10b981"
            ))
            fig_bar.update_layout(
                title="Invested vs Current Value by Fund",
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Fund",
                yaxis_title="Value (INR)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        divider()
        
        # ── Transaction Log ──────────────────────────────────────────
        st.markdown("### Transaction Log & Individual Holdings")
        
        # Format transaction list
        render_html("""
        <div style="background-color:#1a2f5e; color:#ffffff; padding:10px; border-radius:8px 8px 0px 0px; font-weight:bold; font-size:0.9rem;">
            <div style="display:flex; justify-content:space-between; text-align:left;">
                <div style="width:30%;">Fund Name</div>
                <div style="width:15%;">Purchase Date</div>
                <div style="width:15%;">Invested Amount</div>
                <div style="width:15%;">Units Owned</div>
                <div style="width:15%;">Gains / P&L</div>
                <div style="width:10%; text-align:center;">Action</div>
            </div>
        </div>
        """)
        
        for idx, row in df_tx.iterrows():
            pl_color = "#10b981" if row["profit_loss"] >= 0 else "#ef4444"
            render_html(f"""
            <div style="background-color:#ffffff; color:#1a2340; padding:12px; margin-bottom:1px; border-bottom:1px solid #f0f4f8; display:flex; justify-content:space-between; align-items:center; font-size:0.88rem; box-shadow:0px 2px 4px rgba(0,0,0,0.02);">
                <div style="width:30%; font-weight:500;">{row['short_name']}</div>
                <div style="width:15%; color:#475569;">{row['purchase_date'].strftime('%Y-%m-%d')}</div>
                <div style="width:15%; font-weight:600;">₹{row['amount']:,.2f}</div>
                <div style="width:15%; color:#475569;">{row['units']:.4f}</div>
                <div style="width:15%; color:{pl_color}; font-weight:600;">
                    ₹{row['profit_loss']:+,.2f}<br>
                    <span style="font-size:0.75rem; font-weight:400;">({row['profit_loss_pct']:+.2f}%)</span>
                </div>
                <div style="width:10%; text-align:center;">
                </div>
            </div>
            """)
            # Render Streamlit delete button in the same line space via columns
            c_space, c_btn = st.columns([9, 1])
            with c_btn:
                if st.button("🗑️", key=f"del_{row['id']}", help="Delete transaction"):
                    delete_portfolio_transaction(row["id"])
                    st.success("Deleted!")
                    st.rerun()
