# ================================================================
#  charts.py — Reusable Plotly chart components
#  Mutual Fund Analytics | Frontend Components
# ================================================================

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ── Brand color palette ──────────────────────────────────────────
FUND_COLORS = [
    "#3b82f6",  # blue
    "#10b981",  # green
    "#8b5cf6",  # purple
    "#f59e0b",  # amber
    "#ef4444",  # red
    "#0d9488",  # teal
    "#ec4899",  # pink
    "#6366f1",  # indigo
]

CHART_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", size=12, color="#475569"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#e2e8f0",
        borderwidth=1,
        font=dict(size=11),
    ),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#e2e8f0",
        font=dict(size=12, color="#0f1b35"),
    ),
)


def make_nav_trend_chart(df: pd.DataFrame, title: str = "NAV Trend") -> go.Figure:
    """
    Single-fund NAV line chart with gradient fill, smooth curve,
    and styled hover tooltip.
    """
    fig = go.Figure()

    # Ensure date is datetime
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    fund_name = df["scheme_name"].iloc[0] if "scheme_name" in df.columns else "Fund"

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["nav"],
        mode="lines",
        name=fund_name,
        line=dict(color=FUND_COLORS[0], width=2.5, shape="spline", smoothing=0.8),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.07)",
        hovertemplate=(
            "<b>%{x|%d %b %Y}</b><br>"
            "NAV: <b>Rs. %{y:.4f}</b><extra></extra>"
        ),
    ))

    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text=title, font=dict(size=15, color="#0f1b35", weight=700), x=0),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=11),
            tickformat="%b %Y",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(226,232,240,0.6)",
            zeroline=False,
            tickprefix="Rs. ",
            tickfont=dict(size=11),
        ),
        height=380,
    )
    return fig


def make_comparison_chart(df: pd.DataFrame, title: str = "NAV Comparison") -> go.Figure:
    """
    Multi-fund comparison chart. Each fund gets its own colored line.
    Values are normalised to 100 on start date for fair comparison.
    """
    fig = go.Figure()

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    funds = df["scheme_name"].unique()

    for i, fund in enumerate(funds):
        fdf = df[df["scheme_name"] == fund].sort_values("date").copy()
        if fdf.empty:
            continue

        # Normalise to 100 at start for apples-to-apples comparison
        base = fdf["nav"].iloc[0]
        fdf["nav_norm"] = (fdf["nav"] / base) * 100

        color = FUND_COLORS[i % len(FUND_COLORS)]
        short_name = fund[:40] + "..." if len(fund) > 40 else fund

        fig.add_trace(go.Scatter(
            x=fdf["date"],
            y=fdf["nav_norm"],
            mode="lines",
            name=short_name,
            line=dict(color=color, width=2.2, shape="spline", smoothing=0.6),
            hovertemplate=(
                f"<b>{short_name}</b><br>"
                "Date: <b>%{x|%d %b %Y}</b><br>"
                "Normalised: <b>%{y:.2f}</b><extra></extra>"
            ),
        ))

    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text=title, font=dict(size=15, color="#0f1b35", weight=700), x=0),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickformat="%b %Y",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(226,232,240,0.6)",
            zeroline=False,
            ticksuffix="",
            title="Indexed Value (Base=100)",
            tickfont=dict(size=11),
        ),
        height=420,
    )
    return fig


def make_returns_bar_chart(returns_df: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart of fund returns, colour-coded green/red.
    """
    df = returns_df.copy().sort_values("return_pct", ascending=True)
    colors = [FUND_COLORS[1] if v >= 0 else FUND_COLORS[4] for v in df["return_pct"]]

    # Truncate long fund names
    df["short_name"] = df["scheme_name"].apply(
        lambda x: x[:35] + "..." if len(x) > 35 else x
    )

    fig = go.Figure(go.Bar(
        x=df["return_pct"],
        y=df["short_name"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:+.2f}%" for v in df["return_pct"]],
        textposition="outside",
        textfont=dict(size=12, color="#0f1b35"),
        hovertemplate="<b>%{y}</b><br>Return: <b>%{x:.2f}%</b><extra></extra>",
    ))

    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Fund Returns (%)", font=dict(size=15, color="#0f1b35", weight=700), x=0),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(226,232,240,0.6)",
            zeroline=True,
            zerolinecolor="#cbd5e1",
            ticksuffix="%",
        ),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        height=max(280, len(df) * 55),
    )
    return fig


def make_volatility_chart(vol_df: pd.DataFrame) -> go.Figure:
    """
    Scatter plot: return vs volatility (risk-return map).
    """
    df = vol_df.copy()
    df["short_name"] = df["scheme_name"].apply(
        lambda x: x[:30] + "..." if len(x) > 30 else x
    )

    fig = go.Figure()
    for i, row in df.iterrows():
        color = FUND_COLORS[i % len(FUND_COLORS)]
        fig.add_trace(go.Scatter(
            x=[row["volatility"]],
            y=[row["return_pct"]],
            mode="markers+text",
            name=row["short_name"],
            text=[row["short_name"]],
            textposition="top center",
            textfont=dict(size=10),
            marker=dict(size=14, color=color, line=dict(width=2, color="white")),
            hovertemplate=(
                f"<b>{row['short_name']}</b><br>"
                "Volatility: <b>%{x:.2f}%</b><br>"
                "Return: <b>%{y:.2f}%</b><extra></extra>"
            ),
        ))

    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Risk vs Return Map", font=dict(size=15, color="#0f1b35", weight=700), x=0),
        xaxis=dict(
            title="Volatility (Std Dev %)",
            showgrid=True,
            gridcolor="rgba(226,232,240,0.6)",
        ),
        yaxis=dict(
            title="Total Return (%)",
            showgrid=True,
            gridcolor="rgba(226,232,240,0.6)",
            ticksuffix="%",
        ),
        showlegend=False,
        height=360,
    )
    return fig


def make_rolling_return_chart(df: pd.DataFrame, window: int = 30) -> go.Figure:
    """
    Rolling N-day return chart for a single fund.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["rolling_return"] = df["nav"].pct_change(window) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["rolling_return"],
        mode="lines",
        name=f"{window}D Rolling Return",
        line=dict(color=FUND_COLORS[2], width=2, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(139,92,246,0.07)",
        hovertemplate=(
            "<b>%{x|%d %b %Y}</b><br>"
            f"{window}D Return: <b>%{{y:.2f}}%</b><extra></extra>"
        ),
    ))

    # Zero line
    fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8", line_width=1)

    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(
            text=f"{window}-Day Rolling Return (%)",
            font=dict(size=15, color="#0f1b35", weight=700), x=0
        ),
        xaxis=dict(showgrid=False, zeroline=False, tickformat="%b %Y"),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(226,232,240,0.6)",
            ticksuffix="%",
        ),
        height=320,
    )
    return fig
