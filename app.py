import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from datetime import datetime, timezone


# ============================================================
# HELPER
# ============================================================

def render_html(html):
    """
    Render HTML safely without allowing indentation
    to turn the HTML into a Markdown code block.
    """
    cleaned_html = "\n".join(
        line.strip()
        for line in html.splitlines()
        if line.strip()
    )

    st.markdown(
        cleaned_html,
        unsafe_allow_html=True
    )


# ============================================================
# BRAND / TOKENS
# ============================================================

BRAND_NAME = "Dynamic Supply Chain"
BRAND_SUBTITLE = "Operations Intelligence"
BRAND_SLUG = BRAND_NAME.lower().replace(" ", "_")

SHIPPING_MODES = [
    "Standard Class",
    "Second Class",
    "First Class",
    "Same Day"
]

COLOR_TEXT = "#172033"
COLOR_MUTED = "#6b7280"
COLOR_GRID = "#eef1f5"
COLOR_TRACK = "#c7cdd6"
COLOR_PRIMARY = "#23679a"
COLOR_PRIMARY_DARK = "#173d61"
COLOR_PRIMARY_LIGHT = "#8fb4d1"
COLOR_GREEN = "#16794c"
COLOR_RED = "#b42318"

CHART_FONT = dict(family="Inter, sans-serif", size=12, color=COLOR_TEXT)
SPARK_CONFIG = {"displayModeBar": False}


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title=f"{BRAND_NAME} · {BRAND_SUBTITLE}",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "scenario_history" not in st.session_state:
    st.session_state.scenario_history = []


# ============================================================
# DATA PATHS
# ============================================================

SUBSET_PATH = "data/processed/supply_chain_subset.csv"
RECOVERY_PATH = "data/processed/row_level_recovery_results.csv"
EVALUATION_PATH = "data/processed/final_evaluation_results.csv"
ROUTE_PATH = "data/processed/route_data.csv"


# ============================================================
# LOAD DATA
# ============================================================

try:
    df = pd.read_csv(SUBSET_PATH)
    recovery_df = pd.read_csv(RECOVERY_PATH)
    evaluation_df = pd.read_csv(EVALUATION_PATH)
    route_df = pd.read_csv(ROUTE_PATH)
except Exception as exc:
    st.error(
        "Could not load one or more data files. "
        f"Details: {exc}"
    )
    st.stop()


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ==========================================================
   MAIN APPLICATION
   ========================================================== */

.stApp {
    background-color: #f5f7fa;
    color: #172033;
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1450px;
    animation: fadeIn 0.35s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {
    background-color: #111827 !important;
    border-right: 1px solid #1f2937;
    min-width: 280px;
    max-width: 280px;
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.8rem;
}

.sidebar-brand-name {
    font-size: 21px;
    font-weight: 800;
    letter-spacing: 1.4px;
    color: #ffffff;
    margin-bottom: 0;
}

.sidebar-brand-subtitle {
    color: #9ca3af;
    font-size: 12px;
    margin-top: 2px;
    margin-bottom: 26px;
}

.sidebar-heading {
    font-size: 11px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 700;
    margin-bottom: 10px;
    margin-top: 22px;
}

.sidebar-divider {
    border-top: 1px solid #1f2937;
    margin: 18px 0;
}

.sidebar-status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    color: #d1d5db;
    margin-bottom: 8px;
}

.sidebar-status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #34d399;
    flex-shrink: 0;
}

.sidebar-history-item {
    padding: 8px 0;
    border-bottom: 1px solid #1f2937;
}

.sidebar-history-route {
    font-size: 12.5px;
    color: #e5e7eb;
    font-weight: 600;
}

.sidebar-history-time {
    font-size: 11px;
    color: #6b7280;
    margin-top: 2px;
}

.sidebar-history-empty {
    font-size: 12px;
    color: #6b7280;
}

.sidebar-footer {
    color: #6b7280;
    font-size: 11px;
    line-height: 1.6;
}

/* Selectbox */

section[data-testid="stSidebar"]
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 6px !important;
    min-height: 46px !important;
}

section[data-testid="stSidebar"]
div[data-baseweb="select"] * {
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
    opacity: 1 !important;
}

section[data-testid="stSidebar"]
div[data-baseweb="select"] svg {
    fill: #6b7280 !important;
}

/* Dropdown */

div[data-baseweb="popover"] {
    background-color: #ffffff !important;
}

div[data-baseweb="popover"] * {
    color: #172033 !important;
}

/* Radio (workspace nav) */

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: 7px 2px;
}

/* ==========================================================
   HEADINGS
   ========================================================== */

h1,
h2,
h3 {
    color: #172033 !important;
    font-weight: 650 !important;
}

.section-label {
    color: #6b7280;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

.page-title {
    font-size: 28px;
    font-weight: 700;
    color: #172033;
    margin-bottom: 3px;
}

.page-subtitle {
    color: #6b7280;
    font-size: 14px;
    max-width: 640px;
}

.page-header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 14px;
    margin-bottom: 24px;
}

/* Live status pill */

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: #16794c;
    font-weight: 700;
    letter-spacing: 0.4px;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #16794c;
    display: inline-block;
}

.status-timestamp {
    font-size: 11px;
    color: #9aa4b2;
    margin-top: 4px;
    text-align: right;
}

/* ==========================================================
   CARDS + HOVER TRANSITIONS
   ========================================================== */

.metric-card,
.info-card,
.reco-card,
div[data-testid="stMetric"],
div[data-testid="stExpander"] {
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.metric-card:hover,
.info-card:hover,
.reco-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 16px rgba(15,35,60,0.08);
}

.metric-card {
    background: #ffffff;
    border: 1px solid #e1e6ec;
    border-radius: 8px;
    padding: 20px 22px;
    min-height: 108px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.metric-label {
    font-size: 12px;
    color: #6b7280;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.7px;
}

.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: #172033;
    margin-top: 8px;
}

.metric-note {
    font-size: 12px;
    color: #87909e;
    margin-top: 4px;
}

/* Native st.metric styling to match card language */

div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e1e6ec;
    border-radius: 8px;
    padding: 14px 16px 6px 16px;
}

div[data-testid="stMetricLabel"] {
    font-size: 12px !important;
    color: #6b7280 !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

div[data-testid="stMetricValue"] {
    font-size: 22px !important;
    color: #172033 !important;
    font-weight: 700 !important;
}

/* Bordered containers (KPI + simulator cards) */

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 8px !important;
    border-color: #e1e6ec !important;
}

/* ==========================================================
   INFORMATION CARDS
   ========================================================== */

.info-card {
    background: #ffffff;
    border: 1px solid #e1e6ec;
    border-radius: 8px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.025);
}

.info-card-title {
    font-size: 14px;
    font-weight: 700;
    color: #172033;
    margin-bottom: 15px;
}

/* ==========================================================
   STATUS BADGES
   ========================================================== */

.status-disrupted {
    display: inline-block;
    background: #fff1f0;
    color: #b42318 !important;
    border: 1px solid #f5c2c0;
    border-radius: 5px;
    padding: 4px 9px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.status-available {
    display: inline-block;
    background: #edf8f1;
    color: #16794c !important;
    border: 1px solid #b9e2ca;
    border-radius: 5px;
    padding: 4px 9px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* ==========================================================
   RECOMMENDATION CARD
   ========================================================== */

.reco-card {
    background: #ffffff;
    border: 1px solid #dce4ec;
    border-left: 4px solid #23679a;
    border-radius: 7px;
    padding: 22px 24px 6px 24px;
    margin-bottom: 4px;
}

.reco-route {
    font-size: 23px;
    font-weight: 700;
    color: #173d61;
    margin: 8px 0 18px 0;
}

.route-arrow {
    color: #8b96a5;
    padding: 0 10px;
}

.reco-stats {
    display: flex;
    gap: 44px;
    flex-wrap: wrap;
    border-top: 1px solid #eef1f5;
    padding-top: 16px;
    margin-bottom: 16px;
}

.reco-stat-label {
    font-size: 11px;
    color: #8b96a5;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 4px;
}

.reco-stat-value {
    font-size: 19px;
    font-weight: 700;
    color: #172033;
}

/* Buttons */

div[data-testid="stButton"] button {
    background-color: #23679a;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 4px;
}

div[data-testid="stButton"] button:hover {
    background-color: #173d61;
    color: #ffffff;
}

div[data-testid="stDownloadButton"] button {
    background-color: #ffffff;
    color: #23679a;
    border: 1px solid #23679a;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
}

div[data-testid="stDownloadButton"] button:hover {
    background-color: #eef5fb;
    color: #173d61;
}

/* ==========================================================
   WHY THIS ROUTE
   ========================================================== */

.reason-row {
    margin-bottom: 16px;
}

.reason-label-row {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    margin-bottom: 6px;
}

.reason-label {
    color: #43506b;
}

.reason-score {
    color: #172033;
    font-weight: 700;
}

.reason-track {
    background: #eef1f5;
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
}

.reason-fill {
    background: #23679a;
    height: 100%;
    border-radius: 4px;
}

/* ==========================================================
   FOOTER
   ========================================================== */

.footer {
    border-top: 1px solid #dfe4ea;
    margin-top: 40px;
    padding-top: 18px;
    color: #8a94a3;
    font-size: 11px;
    text-align: center;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(f"""
<div class="sidebar-brand-name">{BRAND_NAME}</div>
<div class="sidebar-brand-subtitle">{BRAND_SUBTITLE}</div>
""")

    render_html("""<div class="sidebar-heading">Scenario</div>""")

    st.caption("Shipping disruption")

    disruption_mode = st.selectbox(
        "Shipping Mode Disruption",
        SHIPPING_MODES,
        label_visibility="collapsed"
    )

    render_html("""<div class="sidebar-divider"></div>""")

    render_html("""<div class="sidebar-heading">Workspace</div>""")

    page = st.radio(
        "Navigation",
        [
            "Command Center",
            "Recovery Planning",
            "Network",
            "Performance"
        ],
        label_visibility="collapsed"
    )

    render_html("""<div class="sidebar-divider"></div>""")

    render_html("""<div class="sidebar-heading">Recent Activity</div>""")

    if st.session_state.scenario_history:

        history_html = ""

        for entry in st.session_state.scenario_history:
            history_html += f"""
<div class="sidebar-history-item">
<div class="sidebar-history-route">{entry['mode']} → {entry['recovery_mode']}</div>
<div class="sidebar-history-time">{entry['time']}</div>
</div>
"""

        render_html(history_html)

    else:

        render_html("""<div class="sidebar-history-empty">No scenarios applied yet</div>""")

    render_html("""<div class="sidebar-divider"></div>""")

    render_html("""
<div class="sidebar-heading">System</div>

<div class="sidebar-status-row">
<span class="sidebar-status-dot"></span>
Model online
</div>

<div class="sidebar-status-row">
<span class="sidebar-status-dot"></span>
Data loaded
</div>
""")

    render_html("""<div class="sidebar-divider"></div>""")

    render_html("""
<div class="sidebar-footer">
Academic Prototype<br>
v1.0
</div>
""")


# ============================================================
# CURRENT SCENARIO
# ============================================================

total_records = len(df)

affected_records = len(
    df[df["Shipping Mode"] == disruption_mode]
)

recovery_subset = recovery_df[
    recovery_df["Disrupted Mode"] == disruption_mode
]

evaluation_match = evaluation_df[
    evaluation_df["Disrupted Mode"] == disruption_mode
]

has_recovery_plan = not evaluation_match.empty

if has_recovery_plan:

    evaluation_row = evaluation_match.iloc[0]

    recovery_mode = evaluation_row["Primary Recovery Mode"]
    projected_delay = float(evaluation_row["Recovery Expected Delay"])
    projected_cost = float(evaluation_row["Recovery Avg Estimated Cost"])
    recovery_rate = float(evaluation_row["Recovery Rate (%)"])

else:

    recovery_mode = "N/A"
    projected_delay = 0.0
    projected_cost = 0.0
    recovery_rate = 0.0

current_time = datetime.now(timezone.utc).strftime("%H:%M")

# Per-mode aggregates, used for deltas, sparklines and comparisons

mode_affected = df.groupby("Shipping Mode").size().reindex(SHIPPING_MODES)
mode_avg_transit = df.groupby("Shipping Mode")["Days for shipping (real)"].mean().reindex(SHIPPING_MODES)
mode_delay = evaluation_df.set_index("Disrupted Mode")["Recovery Expected Delay"].reindex(SHIPPING_MODES)
mode_rate = evaluation_df.set_index("Disrupted Mode")["Recovery Rate (%)"].reindex(SHIPPING_MODES)


# ============================================================
# SHARED RENDER HELPERS
# ============================================================

def render_page_header(label, title, subtitle):
    render_html(f"""
<div class="page-header-row">
<div>
<div class="section-label">{label}</div>
<div class="page-title">{title}</div>
<div class="page-subtitle">{subtitle}</div>
</div>
<div>
<span class="status-pill"><span class="status-dot"></span>DATA CONNECTED</span>
<div class="status-timestamp">Last analysis {current_time} UTC</div>
</div>
</div>
""")


def render_recommendation_card(mode, rec_mode, delay, cost, rate, button_key):
    render_html(f"""
<div class="reco-card">
<div class="section-label">Recommended Recovery</div>
<div class="reco-route">
{mode}
<span class="route-arrow">→</span>
{rec_mode}
</div>
<div class="reco-stats">
<div>
<div class="reco-stat-label">Expected delay</div>
<div class="reco-stat-value">{delay:.2f}d</div>
</div>
<div>
<div class="reco-stat-label">Estimated cost</div>
<div class="reco-stat-value">{cost:.2f}</div>
</div>
<div>
<div class="reco-stat-label">Coverage</div>
<div class="reco-stat-value">{rate:.1f}%</div>
</div>
</div>
</div>
""")

    _, btn_col = st.columns([5, 1])

    with btn_col:
        applied = st.button("Apply Scenario", key=button_key, width="stretch")

    if applied:
        st.session_state[f"applied_{button_key}"] = True
        st.session_state.scenario_history.insert(0, {
            "mode": mode,
            "recovery_mode": rec_mode,
            "time": datetime.now(timezone.utc).strftime("%H:%M UTC")
        })
        st.session_state.scenario_history = st.session_state.scenario_history[:5]
        st.rerun()

    if st.session_state.get(f"applied_{button_key}"):
        st.success(f"Scenario applied — {mode} rerouted to {rec_mode}.")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


def build_sparkline(categories, values, highlight, height=48):
    colors = [
        COLOR_PRIMARY_DARK if c == highlight else COLOR_TRACK
        for c in categories
    ]

    fig = go.Figure(go.Bar(
        x=list(categories),
        y=list(values),
        marker_color=colors
    ))

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False
    )

    return fig


def build_delay_chart(evaluation_df, selected_mode, height=320):
    modes = evaluation_df["Disrupted Mode"]
    baseline = evaluation_df["Baseline Avg Delay"]
    recovery = evaluation_df["Recovery Expected Delay"]

    recovery_colors = [
        COLOR_PRIMARY_DARK if m == selected_mode else COLOR_PRIMARY_LIGHT
        for m in modes
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=modes,
        x=baseline,
        name="Baseline",
        orientation="h",
        marker_color=COLOR_TRACK
    ))

    fig.add_trace(go.Bar(
        y=modes,
        x=recovery,
        name="Projected Recovery",
        orientation="h",
        marker_color=recovery_colors
    ))

    fig.update_layout(
        barmode="group",
        height=height,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="left", x=0),
        xaxis=dict(title="Days", gridcolor=COLOR_GRID, zeroline=False),
        yaxis=dict(gridcolor=COLOR_GRID),
        font=CHART_FONT
    )

    return fig


def build_reliability_chart(evaluation_df, selected_mode, height=300):
    modes = evaluation_df["Disrupted Mode"]
    rates = evaluation_df["Baseline Delay Rate (%)"]

    colors = [
        COLOR_RED if m == selected_mode else COLOR_TRACK
        for m in modes
    ]

    fig = go.Figure(go.Bar(
        y=modes,
        x=rates,
        orientation="h",
        marker_color=colors
    ))

    fig.update_layout(
        height=height,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title="Baseline delay rate (%)", gridcolor=COLOR_GRID, zeroline=False),
        yaxis=dict(gridcolor=COLOR_GRID),
        font=CHART_FONT,
        showlegend=False
    )

    return fig


def normalize_inverse(series, value):
    lo, hi = series.min(), series.max()
    if hi - lo == 0:
        return 100.0
    return round(100 * (1 - (value - lo) / (hi - lo)), 1)


def style_gradient_table(data, gradients):
    """
    gradients: dict of {column_name: matplotlib colormap name}
    """
    styler = data.style

    for col, cmap in gradients.items():
        if col in data.columns:
            styler = styler.background_gradient(cmap=cmap, subset=[col])

    styler = styler.format(precision=2)

    try:
        styler = styler.hide(axis="index")
    except Exception:
        pass

    return styler


def build_choropleth(route_df, height=480):
    country_counts = (
        route_df["Order Country"]
        .value_counts()
        .reset_index()
    )
    country_counts.columns = ["Country", "Orders"]

    fig = go.Figure(go.Choropleth(
        locations=country_counts["Country"],
        locationmode="country names",
        z=country_counts["Orders"],
        colorscale=[[0, "#eef5fb"], [1, COLOR_PRIMARY_DARK]],
        marker_line_color="#ffffff",
        marker_line_width=0.5,
        colorbar_title="Orders"
    ))

    fig.update_geos(
        scope="europe",
        showcountries=True,
        countrycolor="#d5dbe3",
        showframe=False,
        bgcolor="rgba(0,0,0,0)"
    )

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#ffffff",
        font=CHART_FONT
    )

    return fig


def build_sankey(recovery_df, selected_mode, height=380):
    flow_counts = (
        recovery_df
        .groupby(["Disrupted Mode", "Recovery Mode"])
        .size()
        .reset_index(name="Count")
    )

    source_labels = sorted(flow_counts["Disrupted Mode"].unique())
    target_labels = sorted(flow_counts["Recovery Mode"].unique())

    all_labels = (
        [f"{s} (disrupted)" for s in source_labels]
        + [f"{t} (recovered)" for t in target_labels]
    )

    source_idx = {s: i for i, s in enumerate(source_labels)}
    target_idx = {t: i + len(source_labels) for i, t in enumerate(target_labels)}

    link_colors = [
        "rgba(35,103,154,0.55)" if s == selected_mode else "rgba(199,205,214,0.35)"
        for s in flow_counts["Disrupted Mode"]
    ]

    node_colors = (
        [COLOR_PRIMARY_DARK] * len(source_labels)
        + [COLOR_GREEN] * len(target_labels)
    )

    fig = go.Figure(go.Sankey(
        node=dict(
            label=all_labels,
            pad=18,
            thickness=14,
            color=node_colors,
            line=dict(color="#ffffff", width=0.5)
        ),
        link=dict(
            source=[source_idx[s] for s in flow_counts["Disrupted Mode"]],
            target=[target_idx[t] for t in flow_counts["Recovery Mode"]],
            value=flow_counts["Count"],
            color=link_colors
        )
    ))

    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#ffffff",
        font=CHART_FONT
    )

    return fig


# ============================================================
# COMMAND CENTER
# ============================================================

if page == "Command Center":

    render_page_header(
        "Network Operations",
        "Command Center",
        "Live view of the current disruption scenario and the recovery plan the model recommends."
    )

    render_html("""<div class="section-label">Scenario at a Glance</div>""")

    avg_affected_all = mode_affected.mean()
    avg_rate_all = mode_rate.mean()
    avg_delay_all = mode_delay.mean()
    avg_transit_all = mode_avg_transit.mean()

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        with st.container(border=True):
            st.metric(
                "Affected orders",
                f"{affected_records:,}",
                delta=f"{affected_records - avg_affected_all:+,.0f} vs avg",
                delta_color="inverse"
            )
            st.plotly_chart(
                build_sparkline(mode_affected.index, mode_affected.values, disruption_mode),
                width="stretch",
                config=SPARK_CONFIG
            )

    with s2:
        with st.container(border=True):
            st.metric(
                "Recoverable",
                f"{recovery_rate:.1f}%",
                delta=f"{recovery_rate - avg_rate_all:+.1f}pp vs avg"
            )
            st.plotly_chart(
                build_sparkline(mode_rate.index, mode_rate.values, disruption_mode),
                width="stretch",
                config=SPARK_CONFIG
            )

    with s3:
        with st.container(border=True):
            st.metric(
                "Projected delay",
                f"{projected_delay:.2f}d",
                delta=f"{projected_delay - avg_delay_all:+.2f}d vs avg",
                delta_color="inverse"
            )
            st.plotly_chart(
                build_sparkline(mode_delay.index, mode_delay.values, disruption_mode),
                width="stretch",
                config=SPARK_CONFIG
            )

    with s4:
        with st.container(border=True):
            st.metric(
                "Avg transit time",
                f"{mode_avg_transit[disruption_mode]:.2f}d",
                delta=f"{mode_avg_transit[disruption_mode] - avg_transit_all:+.2f}d vs avg",
                delta_color="inverse"
            )
            st.plotly_chart(
                build_sparkline(mode_avg_transit.index, mode_avg_transit.values, disruption_mode),
                width="stretch",
                config=SPARK_CONFIG
            )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Compare with another disruption mode"):

        other_modes = [m for m in SHIPPING_MODES if m != disruption_mode]
        compare_mode = st.selectbox("Compare against", other_modes, key="compare_mode_select")

        compare_match = evaluation_df[evaluation_df["Disrupted Mode"] == compare_mode]
        compare_has_plan = not compare_match.empty

        if compare_has_plan:
            compare_row = compare_match.iloc[0]
            c_delay = float(compare_row["Recovery Expected Delay"])
            c_rate = float(compare_row["Recovery Rate (%)"])
        else:
            c_delay, c_rate = 0.0, 0.0

        c_affected = len(df[df["Shipping Mode"] == compare_mode])

        cc1, cc2 = st.columns(2)

        with cc1:
            render_html(f"""<div class="section-label">{disruption_mode}</div>""")
            st.metric("Affected orders", f"{affected_records:,}", delta=f"{affected_records - c_affected:+,}", delta_color="inverse")
            st.metric("Projected delay", f"{projected_delay:.2f}d", delta=f"{projected_delay - c_delay:+.2f}d", delta_color="inverse")
            st.metric("Coverage", f"{recovery_rate:.1f}%", delta=f"{recovery_rate - c_rate:+.1f}pp")

        with cc2:
            render_html(f"""<div class="section-label">{compare_mode}</div>""")
            st.metric("Affected orders", f"{c_affected:,}", delta=f"{c_affected - affected_records:+,}", delta_color="inverse")
            st.metric("Projected delay", f"{c_delay:.2f}d", delta=f"{c_delay - projected_delay:+.2f}d", delta_color="inverse")
            st.metric("Coverage", f"{c_rate:.1f}%", delta=f"{c_rate - recovery_rate:+.1f}pp")

    left, right = st.columns([1, 2])

    with left:

        render_html(f"""
<div class="info-card" style="min-height:230px;">

<div class="section-label">Current Scenario</div>

<div class="info-card-title">{disruption_mode}</div>

<span class="status-disrupted">DISRUPTED</span>

<div style="margin-top:20px;font-size:26px;font-weight:700;color:#172033;">
{affected_records:,}
</div>

<div style="color:#6b7280;font-size:12px;">
transactions affected
</div>

</div>
""")

    with right:

        if has_recovery_plan:

            render_recommendation_card(
                disruption_mode,
                recovery_mode,
                projected_delay,
                projected_cost,
                recovery_rate,
                button_key="cmd_center_apply"
            )

        else:

            render_html(f"""
<div class="info-card" style="min-height:230px;">
<div class="section-label">Recommended Recovery</div>
<div class="info-card-title">No recovery plan available</div>
<div style="color:#6b7280;font-size:13px;">
No alternative shipping mode was identified for {disruption_mode} in the
evaluation results.
</div>
</div>
""")

    with st.expander("Scenario Simulator — what if disruption severity changes?"):

        severity_pct = st.slider(
            "Disruption severity (% of the typical affected volume)",
            min_value=10,
            max_value=150,
            value=100,
            step=5,
            key="severity_slider"
        )

        scaled_affected = round(affected_records * severity_pct / 100)
        scaled_cost = projected_cost * scaled_affected if has_recovery_plan else 0.0

        sim1, sim2, sim3 = st.columns(3)

        with sim1:
            st.metric(
                "Simulated affected orders",
                f"{scaled_affected:,}",
                delta=f"{scaled_affected - affected_records:+,}",
                delta_color="inverse"
            )

        with sim2:
            st.metric("Simulated total recovery cost", f"{scaled_cost:,.2f}")

        with sim3:
            st.metric("Delay per order (unchanged)", f"{projected_delay:.2f}d")

        st.caption(
            "Linear projection scaled from the current recovery plan's average "
            "estimated cost — for exploration only, not a forecast."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""<div class="section-label">Delivery Impact</div>""")

    st.plotly_chart(
        build_delay_chart(evaluation_df, disruption_mode),
        width="stretch"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""<div class="section-label">Recovery Activity</div>""")

    activity_cols = [
        c for c in ["Record Id", "Disrupted Mode", "Recovery Mode", "Estimated Cost", "Heuristic Score"]
        if c in recovery_df.columns
    ]

    activity_sample = recovery_subset[activity_cols].head(6) if activity_cols else pd.DataFrame()

    if not activity_sample.empty:
        styled_activity = style_gradient_table(
            activity_sample,
            {"Estimated Cost": "Reds", "Heuristic Score": "Greens"}
        )
        st.dataframe(styled_activity, width="stretch")
    else:
        st.caption("No recovery decisions recorded for this scenario.")


# ============================================================
# RECOVERY PLANNING
# ============================================================

elif page == "Recovery Planning":

    render_page_header(
        "Recovery Planning",
        "Adaptive Recovery Plan",
        "Candidate shipping modes are evaluated on historical delivery performance, "
        "projected delay and modeled logistics cost."
    )

    if has_recovery_plan:

        render_recommendation_card(
            disruption_mode,
            recovery_mode,
            projected_delay,
            projected_cost,
            recovery_rate,
            button_key="recovery_plan_apply"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        cost_score = normalize_inverse(evaluation_df["Recovery Avg Estimated Cost"], projected_cost)
        delay_score = normalize_inverse(evaluation_df["Recovery Expected Delay"], projected_delay)
        reliability_score = round(float(recovery_rate), 1)

        reasons = [
            ("Cost impact", cost_score),
            ("Historical reliability", reliability_score),
            ("Delay impact", delay_score),
        ]

        reason_rows = ""
        for label, score in reasons:
            reason_rows += f"""
<div class="reason-row">
<div class="reason-label-row">
<span class="reason-label">{label}</span>
<span class="reason-score">{score:.0f}</span>
</div>
<div class="reason-track">
<div class="reason-fill" style="width:{max(score, 0):.0f}%;"></div>
</div>
</div>
"""

        render_html(f"""
<div class="info-card">
<div class="info-card-title">Why this route?</div>
{reason_rows}
</div>
""")

        st.markdown("<br>", unsafe_allow_html=True)

        report_text = (
            f"{BRAND_NAME} — Recovery Plan Report\n"
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            f"Disrupted Mode: {disruption_mode}\n"
            f"Recommended Recovery Mode: {recovery_mode}\n"
            f"Affected Orders: {affected_records}\n"
            f"Projected Delay: {projected_delay:.2f} days\n"
            f"Projected Cost: {projected_cost:.2f}\n"
            f"Coverage: {recovery_rate:.1f}%\n"
        )

        dl1, dl2 = st.columns(2)

        with dl1:
            st.download_button(
                "Download Scenario Report (.txt)",
                data=report_text,
                file_name=f"{BRAND_SLUG}_{disruption_mode.replace(' ', '_').lower()}_report.txt",
                mime="text/plain",
                width="stretch"
            )

        with dl2:
            if not recovery_subset.empty:
                st.download_button(
                    "Download Recovered Transactions (.csv)",
                    data=recovery_subset.to_csv(index=False),
                    file_name=f"{BRAND_SLUG}_{disruption_mode.replace(' ', '_').lower()}_transactions.csv",
                    mime="text/csv",
                    width="stretch"
                )

    else:

        render_html(f"""
<div class="info-card">
<div class="section-label">Recovery Route</div>
<div class="info-card-title">No recovery plan available</div>
<div style="color:#6b7280;font-size:13px;">
No alternative shipping mode was identified for {disruption_mode} in the
evaluation results.
</div>
</div>
""")

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""<div class="section-label">Recovered Transactions</div>""")

    display_cols = [
        "Record Id",
        "Disrupted Mode",
        "Recovery Mode",
        "Estimated Cost",
        "Heuristic Score"
    ]

    available_cols = [
        c for c in display_cols
        if c in recovery_df.columns
    ]

    if available_cols:

        sample = recovery_subset[available_cols].head(15)

        if not sample.empty:
            styled_sample = style_gradient_table(
                sample,
                {"Estimated Cost": "Reds", "Heuristic Score": "Greens"}
            )
            st.dataframe(styled_sample, width="stretch")
        else:
            st.caption("No record-level recovery decisions for this scenario.")


# ============================================================
# NETWORK
# ============================================================

elif page == "Network":

    render_page_header(
        "Network Operations",
        "European Logistics Network",
        "Geographic hierarchy used to represent the available supply-chain structure "
        "in the DataCo dataset."
    )

    c1, c2, c3, c4 = st.columns(4)

    network_stats = [
        ("Regions", 4),
        ("Countries", 36),
        ("Cities", 1131),
        ("Orders", 7817)
    ]

    for col, (label, value) in zip([c1, c2, c3, c4], network_stats):

        with col:

            render_html(f"""
<div class="metric-card">
<div class="metric-label">{label}</div>
<div class="metric-value">{value:,}</div>
<div class="metric-note">Network entities</div>
</div>
""")

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""
<div class="section-label">Network Structure</div>

<div class="info-card">

<div style="
display:flex;
align-items:center;
justify-content:center;
gap:15px;
flex-wrap:wrap;
padding:25px 5px;
">

<div style="padding:14px 22px;border:1px solid #cbd5df;background:#f8fafc;border-radius:6px;font-weight:600;">
Market
</div>

<div style="color:#9aa4b2;">→</div>

<div style="padding:14px 22px;border:1px solid #cbd5df;background:#f8fafc;border-radius:6px;font-weight:600;">
Region
</div>

<div style="color:#9aa4b2;">→</div>

<div style="padding:14px 22px;border:1px solid #cbd5df;background:#f8fafc;border-radius:6px;font-weight:600;">
Country
</div>

<div style="color:#9aa4b2;">→</div>

<div style="padding:14px 22px;border:1px solid #cbd5df;background:#f8fafc;border-radius:6px;font-weight:600;">
City
</div>

<div style="color:#9aa4b2;">→</div>

<div style="padding:14px 22px;border:1px solid #23679a;background:#eef5fb;color:#23679a;border-radius:6px;font-weight:600;">
Order
</div>

</div>

<div style="border-top:1px solid #e5e7eb;margin-top:10px;padding-top:15px;font-size:12px;color:#6b7280;">
The dataset does not contain explicit supplier, factory or warehouse entities.
The network therefore uses the geographic hierarchy available in the
transaction records.
</div>

</div>
""")

    render_html("""<div class="section-label">Geographic Distribution</div>""")

    st.caption(
        "Order volume by country. Country names are matched against Plotly's "
        "built-in map data, so a handful of names may not resolve if they differ "
        "from the standard English spelling."
    )

    st.plotly_chart(
        build_choropleth(route_df),
        width="stretch"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""<div class="section-label">Network Graph</div>""")

    st.caption(
        "A sampled view of the region → country → city hierarchy, kept small so the graph stays readable."
    )

    sample_routes = route_df.head(150)

    G = nx.DiGraph()
    node_level = {}

    for _, row in sample_routes.iterrows():

        region = str(row["Order Region"])
        country = str(row["Order Country"])
        city = str(row["Order City"])

        G.add_edge(region, country)
        G.add_edge(country, city)

        node_level.setdefault(region, "Region")
        node_level.setdefault(country, "Country")
        node_level.setdefault(city, "City")

    pos = nx.spring_layout(G, seed=42, k=0.6)

    edge_x, edge_y = [], []

    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=0.6, color="#d5dbe3"),
        hoverinfo="none",
        showlegend=False
    )

    level_style = {
        "Region": dict(color=COLOR_PRIMARY_DARK, size=18),
        "Country": dict(color=COLOR_PRIMARY, size=10),
        "City": dict(color=COLOR_PRIMARY_LIGHT, size=5),
    }

    node_traces = [edge_trace]

    for level, style in level_style.items():

        nodes = [n for n in G.nodes() if node_level.get(n) == level]

        node_traces.append(go.Scatter(
            x=[pos[n][0] for n in nodes],
            y=[pos[n][1] for n in nodes],
            mode="markers",
            marker=dict(size=style["size"], color=style["color"], line=dict(width=0.5, color="#ffffff")),
            text=nodes,
            hoverinfo="text",
            name=level
        ))

    network_fig = go.Figure(data=node_traces)

    network_fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=12)),
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=520,
        font=CHART_FONT
    )

    st.plotly_chart(network_fig, width="stretch")


# ============================================================
# PERFORMANCE
# ============================================================

elif page == "Performance":

    render_page_header(
        "Analytics",
        "Disruption & Recovery Performance",
        "Comparison of baseline delivery behavior and projected recovery performance "
        "across shipping modes."
    )

    render_html("""<div class="section-label">Delay Comparison</div>""")

    st.plotly_chart(
        build_delay_chart(evaluation_df, disruption_mode, height=350),
        width="stretch"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""<div class="section-label">Historical Service Reliability</div>""")

    st.plotly_chart(
        build_reliability_chart(evaluation_df, disruption_mode),
        width="stretch"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""<div class="section-label">Recovery Flow Overview</div>""")

    st.caption(
        f"How every disrupted transaction in the evaluation set was rerouted. "
        f"{disruption_mode} flows are highlighted."
    )

    if "Disrupted Mode" in recovery_df.columns and "Recovery Mode" in recovery_df.columns:
        st.plotly_chart(
            build_sankey(recovery_df, disruption_mode),
            width="stretch"
        )
    else:
        st.caption("Recovery mode data is not available to build the flow diagram.")

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""<div class="section-label">Recovery Strategy Summary</div>""")

    summary_columns = [
        "Disrupted Mode",
        "Affected Records",
        "Recovered Records",
        "Recovery Rate (%)",
        "Baseline Avg Delay",
        "Recovery Expected Delay",
        "Recovery Avg Estimated Cost",
        "Primary Recovery Mode"
    ]

    summary = evaluation_df[summary_columns].copy()

    summary.columns = [
        "Disrupted Mode",
        "Affected",
        "Recovered",
        "Recovery Rate %",
        "Baseline Delay",
        "Projected Delay",
        "Projected Cost",
        "Recovery Mode"
    ]

    styled_summary = style_gradient_table(
        summary,
        {
            "Recovery Rate %": "Greens",
            "Projected Delay": "Oranges",
            "Projected Cost": "Reds"
        }
    )

    st.dataframe(styled_summary, width="stretch")

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""
<div class="section-label">Model Assumptions</div>

<div class="info-card">

<div class="info-card-title">Interpretation & Limitations</div>

<ul style="color:#596575;font-size:13px;line-height:1.8;">

<li>Recovery decisions are generated at the individual transaction level.</li>

<li>A 100% recovery rate means an alternative shipping mode was identified for
every affected record; it does not guarantee on-time delivery.</li>

<li>Projected logistics cost is a modeled simulation parameter and is not an
actual transportation cost contained in the dataset.</li>

<li>Alternative shipping-mode performance represents a counterfactual
simulation based on historical mode profiles.</li>

<li>The DataCo dataset does not explicitly represent suppliers, factories
or warehouses.</li>

</ul>

</div>
""")


# ============================================================
# FOOTER
# ============================================================

render_html(f"""
<div class="footer">
{BRAND_NAME} · Disruption Recovery & Adaptive Logistics Planning
<br>
Academic Project · DataCo Smart Supply Chain Dataset
</div>
""")