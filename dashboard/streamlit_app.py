# ================================================================
#  streamlit_app.py — Main Dashboard Entry Point
#  Mutual Fund Analytics | Premium Fintech UI
#  Run: streamlit run dashboard/streamlit_app.py
# ================================================================

import sys
import traceback
from pathlib import Path

import streamlit as st
import pandas as pd

# ── Path setup (must happen before any local imports) ────────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Page config (MUST be the very first Streamlit call) ──────────
st.set_page_config(
    page_title="MF Analytics | Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Import all page modules at the TOP (not inside conditionals) ─
# This avoids silent import failures during navigation.
from frontend.components.metrics_cards import kpi_card, page_header, divider
from frontend.components.filters import filter_df_by_period
from frontend.components.charts import make_comparison_chart

import dashboard.pages.fund_analysis        as _page_fa
import dashboard.pages.nav_comparison       as _page_nc
import dashboard.pages.performance_insights as _page_pi
import dashboard.pages.performance_scorecard as _page_ps
import dashboard.pages.portfolio_tracker    as _page_pt


# ================================================================
# THEME INJECTION
# ================================================================

def inject_css() -> None:
    """Load and inject the premium CSS theme into the Streamlit app."""
    css_path = ROOT / "frontend" / "styles" / "theme.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("theme.css not found — using default Streamlit styles.")

inject_css()


# ================================================================
# DATA LOADING  (cached — loads only once per session)
# ================================================================

from sql.db_manager import DB_PATH, get_combined_nav_data_from_db


@st.cache_data(show_spinner="⏳ Loading NAV data from database…")
def load_nav_data() -> pd.DataFrame:
    """
    Query the combined NAV history from SQLite and return a clean DataFrame.
    """
    if not DB_PATH.exists():
        st.error(
            f"**SQLite Database file not found.**\n\n"
            f"Expected path: `{DB_PATH}`\n\n"
            "Run `python sql/load_data.py` first to generate and seed it."
        )
        st.stop()

    try:
        df = get_combined_nav_data_from_db()
    except Exception as exc:
        st.error(f"**Failed to load data from database:** {exc}")
        st.stop()
        
    return df


df_all = load_nav_data()


# ================================================================
# SESSION STATE — initialise navigation state once
# ================================================================

if "active_page" not in st.session_state:
    st.session_state.active_page = "overview"


# ================================================================
# SIDEBAR
# ================================================================

with st.sidebar:

    # ── Logo / Branding ──────────────────────────────────────────
    st.markdown("""
    <div class="top-logo-bar">
        <div style="font-size:2rem;">📊</div>
        <div>
            <div class="logo-text-main">MF Analytics</div>
            <div class="logo-text-sub">Professional Suite</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Navigation buttons ────────────────────────────────────────
    st.markdown("**NAVIGATION**")

    NAV_PAGES = [
        ("🏠  Overview",             "overview"),
        ("🔍  Fund Analysis",        "fund_analysis"),
        ("⚖️  NAV Comparison",       "nav_comparison"),
        ("💡  Performance Insights", "performance_insights"),
        ("🏆  Performance Scorecard", "performance_scorecard"),
        ("💼  Portfolio Tracker",     "portfolio_tracker"),
    ]

    for label, page_key in NAV_PAGES:
        # Highlight the active page button
        is_active = st.session_state.active_page == page_key
        btn_style = (
            "background:rgba(99,179,237,0.28)!important;"
            "border-color:rgba(99,179,237,0.6)!important;"
            "color:#ffffff!important;"
        ) if is_active else ""

        if btn_style:
            st.markdown(f"<style>div[data-testid='stButton'] button[kind='secondary']"
                        f"{{transition:none}}</style>", unsafe_allow_html=True)

        clicked = st.button(label, key=f"nav_btn_{page_key}", use_container_width=True)
        if clicked and st.session_state.active_page != page_key:
            st.session_state.active_page = page_key
            st.rerun()   # ← force immediate re-render with the new page

    st.markdown("---")

    # ── Global period filter ──────────────────────────────────────
    st.markdown("**QUICK PERIOD FILTER**")
    PERIOD_OPTS = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "3Y": 1095, "All": 99999}
    selected_period_label = st.radio(
        "period_radio",
        list(PERIOD_OPTS.keys()),
        index=3,
        horizontal=True,
        label_visibility="collapsed",
        key="sidebar_period",
    )
    selected_days = PERIOD_OPTS[selected_period_label]

    st.markdown("---")

    # ── Dataset info ──────────────────────────────────────────────
    st.markdown("**DATASET INFO**")
    st.markdown(f"""
    <div style='font-size:0.78rem; color:#94a3b8; line-height:1.8;'>
    Funds &nbsp;&nbsp;: <strong style='color:#c8d8f0'>{df_all['scheme_name'].nunique()}</strong><br>
    Records : <strong style='color:#c8d8f0'>{len(df_all):,}</strong><br>
    From &nbsp;&nbsp;&nbsp;: <strong style='color:#c8d8f0'>{df_all['date'].min().strftime('%d %b %Y')}</strong><br>
    To &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <strong style='color:#c8d8f0'>{df_all['date'].max().strftime('%d %b %Y')}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.68rem;color:#475569;text-align:center;'>"
        "Data: MFAPI.in &nbsp;|&nbsp; Built with Streamlit"
        "</div>",
        unsafe_allow_html=True,
    )


# ================================================================
# OVERVIEW PAGE HELPERS
# ================================================================

def compute_kpis(df: pd.DataFrame, days: int) -> dict:
    """Compute top-level KPI metrics from the dataset."""
    df_f = filter_df_by_period(df, days)

    latest_navs = (
        df_f.sort_values("date")
        .groupby("scheme_name")["nav"]
        .last()
    )

    returns = {}
    for fund in df_f["scheme_name"].unique():
        fdf = df_f[df_f["scheme_name"] == fund].sort_values("date")
        if len(fdf) < 2:
            continue
        base = fdf["nav"].iloc[0]
        if base != 0:
            returns[fund] = (fdf["nav"].iloc[-1] / base - 1) * 100

    best_fund  = max(returns, key=returns.get) if returns else "-"
    worst_fund = min(returns, key=returns.get) if returns else "-"

    return {
        "total_funds"  : df_f["scheme_name"].nunique(),
        "avg_nav"      : latest_navs.mean(),
        "highest_nav"  : latest_navs.max(),
        "highest_name" : latest_navs.idxmax() if not latest_navs.empty else "-",
        "lowest_nav"   : latest_navs.min(),
        "lowest_name"  : latest_navs.idxmin() if not latest_navs.empty else "-",
        "date_from"    : df_f["date"].min().strftime("%d %b %Y"),
        "date_to"      : df_f["date"].max().strftime("%d %b %Y"),
        "best_fund"    : best_fund,
        "best_return"  : returns.get(best_fund, 0),
        "total_records": len(df_f),
    }


def show_overview() -> None:
    """Render the Overview / Home page."""
    page_header(
        "Mutual Fund Analytics",
        f"Live NAV dashboard  |  Period: {selected_period_label}  |  "
        f"As of {df_all['date'].max().strftime('%d %b %Y')}"
    )

    kpis = compute_kpis(df_all, selected_days)

    # ── KPI Cards ─────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        kpi_card("Total Funds", str(kpis["total_funds"]),
                 "🏦", "Tracked live", "blue")
    with c2:
        kpi_card("Avg NAV", f"Rs.{kpis['avg_nav']:.2f}",
                 "📈", "Across all funds", "teal")
    with c3:
        kpi_card("Highest NAV", f"Rs.{kpis['highest_nav']:.2f}",
                 "🏆", kpis["highest_name"][:22] + "...", "green")
    with c4:
        kpi_card("Lowest NAV", f"Rs.{kpis['lowest_nav']:.2f}",
                 "📉", kpis["lowest_name"][:22] + "...", "red")
    with c5:
        best_ret = kpis["best_return"]
        kpi_card("Best Return", f"{best_ret:+.1f}%",
                 "⭐", kpis["best_fund"][:22] + "...", "purple",
                 badge=f"{best_ret:+.1f}%", badge_up=(best_ret >= 0))
    with c6:
        kpi_card("Records", f"{kpis['total_records']:,}",
                 "🗄️", f"{kpis['date_from']} — {kpis['date_to']}", "orange")

    st.markdown("<br>", unsafe_allow_html=True)
    divider()

    # ── All-funds normalised chart ─────────────────────────────────
    st.markdown(
        '<div class="section-header">📈 Fund Performance (Normalised to 100)</div>',
        unsafe_allow_html=True,
    )
    df_filtered = filter_df_by_period(df_all, selected_days)
    fig = make_comparison_chart(df_filtered, f"All Funds — {selected_period_label} Period")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    divider()

    # ── Returns summary table ──────────────────────────────────────
    st.markdown(
        '<div class="section-header">📋 Returns Summary Table</div>',
        unsafe_allow_html=True,
    )
    rows = []
    for fund in df_all["scheme_name"].unique():
        fdf = filter_df_by_period(
            df_all[df_all["scheme_name"] == fund], selected_days
        ).sort_values("date")
        if len(fdf) < 2:
            continue
        first_nav = fdf["nav"].iloc[0]
        last_nav  = fdf["nav"].iloc[-1]
        if first_nav == 0:
            continue
        ret_pct = (last_nav / first_nav - 1) * 100
        rows.append({
            "Fund"       : fund[:60],
            "Start NAV"  : f"Rs. {first_nav:.4f}",
            "Latest NAV" : f"Rs. {last_nav:.4f}",
            "Return (%)" : f"{ret_pct:+.2f}%",
            "Direction"  : "↑" if ret_pct >= 0 else "↓",
        })

    summary_df = pd.DataFrame(rows).sort_values("Return (%)", ascending=False)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # Download overview table
    csv_bytes = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download Returns Table as CSV",
        data=csv_bytes,
        file_name="overview_returns.csv",
        mime="text/csv",
        key="dl_overview",
    )


# ================================================================
# PAGE ROUTING  — dispatch to the correct page render function
# ================================================================

ACTIVE = st.session_state.active_page

try:
    if ACTIVE == "overview":
        show_overview()

    elif ACTIVE == "fund_analysis":
        _page_fa.show(df_all, selected_days)

    elif ACTIVE == "nav_comparison":
        _page_nc.show(df_all, selected_days)

    elif ACTIVE == "performance_insights":
        _page_pi.show(df_all, selected_days)

    elif ACTIVE == "performance_scorecard":
        _page_ps.show(df_all, selected_days)

    elif ACTIVE == "portfolio_tracker":
        _page_pt.show(df_all, selected_days)

    else:
        # Fallback: unknown state — reset to overview
        st.session_state.active_page = "overview"
        st.rerun()

except Exception as exc:
    # ── Friendly error display (replaces blank page) ───────────────
    st.error("⚠️ An error occurred while rendering this page.")
    with st.expander("🔍 Show error details (for debugging)"):
        st.code(traceback.format_exc(), language="python")
    st.info(
        "👈 Try selecting a different page from the sidebar, "
        "or reload the app. If this persists, check your data files."
    )
