# ================================================================
#  metrics_cards.py — Custom KPI card HTML components
#  Mutual Fund Analytics | Frontend Components
# ================================================================

import streamlit as st

def render_html(html_str: str) -> None:
    """Helper to strip leading/trailing whitespace from each line of HTML to prevent Streamlit markdown parser bugs."""
    clean_html = "\n".join(line.strip() for line in html_str.split("\n"))
    st.markdown(clean_html, unsafe_allow_html=True)


def kpi_card(label: str, value: str, icon: str = "📊",
             sub: str = "", color: str = "blue",
             badge: str = "", badge_up: bool = True) -> None:
    """
    Render a premium KPI card using HTML injection.

    Parameters
    ----------
    label    : Card title (e.g. "Total Funds")
    value    : Main metric value (e.g. "6")
    icon     : Emoji icon displayed at top
    sub      : Smaller subtitle below value
    color    : Accent color class: blue|green|purple|orange|red|teal
    badge    : Optional badge text (e.g. "+5.2%")
    badge_up : True = green badge, False = red badge
    """
    badge_html = ""
    if badge:
        cls = "kpi-badge-up" if badge_up else "kpi-badge-down"
        badge_html = f'<span class="{cls}">{badge}</span>'

    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""

    html = f"""
    <div class="kpi-card {color}">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
        {badge_html}
    </div>
    """
    render_html(html)


def insight_card(title: str, value: str, detail: str = "",
                 color: str = "blue") -> None:
    """
    Render an auto-insight card with a left accent border.

    Parameters
    ----------
    title  : Small label (e.g. "BEST PERFORMER")
    value  : Main text (e.g. "Nippon Large Cap")
    detail : Supporting detail line
    color  : Accent: blue|green|purple|orange|red
    """
    detail_html = f'<div class="insight-detail">{detail}</div>' if detail else ""
    html = f"""
    <div class="insight-card {color}">
        <div class="insight-title">{title}</div>
        <div class="insight-value">{value}</div>
        {detail_html}
    </div>
    """
    render_html(html)


def risk_badge(level: str) -> str:
    """
    Return an HTML risk badge string for embedding.
    level: 'Low' | 'Medium' | 'High'
    """
    css_class = f"risk-{level.lower()}"
    return f'<span class="{css_class}">{level} Risk</span>'


def section_header(icon: str, title: str) -> None:
    """Render a styled section header with icon."""
    st.markdown(
        f'<div class="section-header">{icon} {title}</div>',
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "") -> None:
    """Render a large page title + subtitle."""
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def divider() -> None:
    """Render a styled horizontal divider."""
    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)


def stat_row(items: list[dict]) -> None:
    """
    Render a horizontal row of mini stat items.

    items: list of dicts with keys: label, value, delta (optional)
    Example: [{"label": "1Y Return", "value": "18.5%", "delta": "+2.1%"}]
    """
    cols_html = ""
    for item in items:
        delta_html = ""
        if "delta" in item:
            is_up = not item["delta"].startswith("-")
            cls = "kpi-badge-up" if is_up else "kpi-badge-down"
            delta_html = f'<span class="{cls}" style="margin-left:6px">{item["delta"]}</span>'

        cols_html += f"""
        <div style="flex:1; text-align:center; padding:0 0.5rem;">
            <div style="font-size:0.7rem;font-weight:600;color:#64748b;
                        text-transform:uppercase;letter-spacing:0.07em;
                        margin-bottom:0.2rem;">{item['label']}</div>
            <div style="font-size:1.1rem;font-weight:700;color:#0f1b35;">
                {item['value']}{delta_html}
            </div>
        </div>
        """

    html = f"""
    <div style="display:flex; background:#ffffff; border-radius:12px;
                padding:1rem 0.5rem; box-shadow:0 1px 6px rgba(15,27,53,0.07);
                border:1px solid #e2e8f0; margin-bottom:1rem;">
        {cols_html}
    </div>
    """
    render_html(html)


def fund_info_card(scheme_name: str, scheme_code: int,
                   date_range: str, total_records: int,
                   risk_level: str = "Medium") -> None:
    """
    Render a fund information summary card.
    """
    rb = risk_badge(risk_level)
    html = f"""
    <div class="chart-card" style="margin-bottom:1rem;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div style="font-size:1.05rem; font-weight:700; color:#0f1b35;
                            margin-bottom:0.5rem;">{scheme_name}</div>
                <div style="font-size:0.8rem; color:#64748b;">
                    Date Range: <strong>{date_range}</strong> &nbsp;|&nbsp;
                    Records: <strong>{total_records:,}</strong>
                </div>
            </div>
            <div style="padding-top:0.2rem;">{rb}</div>
        </div>
    </div>
    """
    render_html(html)
