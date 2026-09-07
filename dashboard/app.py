"""
RealRich PPP: Institutional Wealth Econometrics & Interactive Analytics Suite.
A flagship portfolio application evaluating billionaire net worth through Purchasing Power Parity (PPP),
macroeconomic currency sensitivity, and unsupervised ML archetype clustering.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure project root is available on path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from src.analytics import compute_decomposed_ppp_wealth
    from src.models.clustering import segment_billionaires, segment_billionaires_gmm
    from src.sensitivity import monte_carlo_fx_simulation
    from src.data_loaders import get_ppp_factors_with_fallback
except ImportError:
    try:
        from analytics import compute_decomposed_ppp_wealth
        from models.clustering import segment_billionaires, segment_billionaires_gmm
        from sensitivity import monte_carlo_fx_simulation
        from data_loaders import get_ppp_factors_with_fallback
    except ImportError:
        compute_decomposed_ppp_wealth = None
        segment_billionaires = None
        segment_billionaires_gmm = None
        monte_carlo_fx_simulation = None
        get_ppp_factors_with_fallback = None


# ──────────────────────────────────────────────────────────────────────────────
# 1. PAGE CONFIG & MODERN DESIGN SYSTEM
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RealRich PPP | Billionaire Wealth Econometrics",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom theme.css asset if present
css_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "theme.css")
if os.path.exists(css_file):
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inject modern typography, glassmorphism card styling, and custom theme tokens
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 95% !important;
    }
    
    /* Hero Banner Styling */
    .hero-badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.15), rgba(99, 102, 241, 0.25));
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 9999px;
        color: #38BDF8;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }
    
    .hero-title {
        font-size: 2.35rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #FFFFFF 30%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.4rem;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 400;
        line-height: 1.5;
        margin-bottom: 1.5rem;
    }
    
    /* 1. Metric Cards Truncation & Flexible Wrap */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 0.75rem !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) > div[data-testid="column"] {
        min-width: 200px !important;
        flex: 1 1 200px !important;
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(148, 163, 184, 0.15);
        padding: 1.1rem 1rem;
        border-radius: 1rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
        min-width: 0 !important;
        width: 100% !important;
        overflow: visible !important;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    
    /* Prevent ellipsis cutting across metric elements */
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricDelta"] {
        text-overflow: unset !important;
        white-space: normal !important;
        overflow: visible !important;
        word-break: break-word !important;
    }
    
    [data-testid="stMetricLabel"],
    div[data-testid="stMetric"] label {
        color: #94A3B8 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-size: clamp(1.1rem, 2vw, 1.4rem) !important;
        line-height: 1.25 !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
    }
    
    /* 2. Tab Bar Spillover & Flexible Wrap */
    div[data-baseweb="tab-list"] {
        flex-wrap: wrap !important;
        gap: 4px !important;
    }
    
    div[data-testid="stTabs"] button,
    div[data-baseweb="tab-list"] button {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        padding: 6px 10px !important;
        color: #94A3B8 !important;
        border-radius: 0.5rem !important;
    }
    
    div[data-testid="stTabs"] button[aria-selected="true"],
    div[data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #38BDF8 !important;
        border-bottom: 2px solid #38BDF8 !important;
    }
    
    /* Custom Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    /* Footer Note */
    .footer-text {
        color: #64748B;
        font-size: 0.8rem;
        text-align: center;
        padding: 2rem 0 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 2. DATA INGESTION & ROBUST DATA PIPELINE
# ──────────────────────────────────────────────────────────────────────────────
ISO3_MAP = {
    "United States": "USA",
    "China": "CHN",
    "France": "FRA",
    "India": "IND",
    "Mexico": "MEX",
    "Germany": "DEU",
    "Spain": "ESP",
    "Canada": "CAN",
    "Austria": "AUT",
    "Japan": "JPN",
    "Italy": "ITA",
    "Australia": "AUS",
    "Indonesia": "IDN",
    "United Kingdom": "GBR",
    "Russia": "RUS",
    "Hong Kong": "HKG",
    "Belgium": "BEL",
}

@st.cache_data
def load_data():
    """Load and normalize the PPP master dataset with safety fallbacks."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        "data/processed/top50_nominal_and_ppp.csv",
        "data/output/top50_nominal_and_ppp.csv",
        os.path.join(base_dir, "data", "richest_ppp.csv"),
        os.path.join(REPO_ROOT, "data", "processed", "top50_nominal_and_ppp.csv"),
    ]
    
    df = None
    for path in candidates:
        if os.path.exists(path):
            df = pd.read_csv(path)
            break
            
    if df is None:
        st.error("🚨 Master dataset not found. Run `python src/process_data.py` to generate clean data.")
        return None

    # Normalization mapping for diverse schema compatibility
    col_map = {
        "net_worth_PPP_intl$": "net_worth_ppp",
        "net_worth_USD": "net_worth_usd",
        "net_worth_usd_billion": "net_worth_usd",
        "percent_difference_vs_nominal_USD": "ppp_uplift_pct",
        "pct_change_vs_nominal": "ppp_uplift_pct",
        "rank_nominal": "rank",
        "primary_country": "country",
        "PPP_conversion_factor": "ppp_factor",
        "exchange_rate_local_per_USD": "fx_rate",
    }
    for old_col, new_col in col_map.items():
        if old_col in df.columns and new_col not in df.columns:
            df = df.rename(columns={old_col: new_col})

    # Deduplicate columns to prevent DataFrame indexing collisions
    df = df.loc[:, ~df.columns.duplicated()].copy()

    # Derived types and calculations
    if "rank" not in df.columns and "rank_nominal" in df.columns:
        df["rank"] = df["rank_nominal"].astype(int)
    elif "rank" in df.columns:
        df["rank"] = df["rank"].astype(int)

    if "ppp_uplift_pct" not in df.columns and "net_worth_ppp" in df.columns and "net_worth_usd" in df.columns:
        df["ppp_uplift_pct"] = (
            (df["net_worth_ppp"] - df["net_worth_usd"]) / df["net_worth_usd"] * 100
        ).round(1)

    if "net_worth_ppp" in df.columns and "rank_ppp" not in df.columns:
        df["rank_ppp"] = df["net_worth_ppp"].rank(ascending=False, method="min").astype(int)

    if "rank_change" not in df.columns and "rank" in df.columns and "rank_ppp" in df.columns:
        df["rank_change"] = df["rank"] - df["rank_ppp"]

    # Assign ISO-3 codes for high-precision choropleth maps
    df["iso_alpha"] = df["country"].map(ISO3_MAP).fillna("USA")

    # Compute multi-tier institutional decomposed PPP metrics if engine available
    if compute_decomposed_ppp_wealth is not None:
        try:
            df = compute_decomposed_ppp_wealth(df)
        except Exception:
            pass

    return df


@st.cache_data
def load_config():
    """Load macroeconomic conversion config."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(REPO_ROOT, "configs", "ppp_rates.json"),
        os.path.join(base_dir, "..", "configs", "ppp_rates.json"),
        "configs/ppp_rates.json",
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    return {
        "analysis_date": "January 2026",
        "data_source": "Forbes Real-Time Index",
        "ppp_source": "World Bank ICP 2024/2025 WDI"
    }


# Load Core State
df = load_data()
config = load_config()

if df is None:
    st.stop()


# ──────────────────────────────────────────────────────────────────────────────
# 3. GLOBAL CONTROLS & SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💎 RealRich PPP Engine")
    st.caption("Quantitative Wealth Econometrics & BI Suite")
    st.markdown("---")

    st.subheader("⚙️ Filter & Parameters")
    
    # Methodology Framework Selector
    valuation_model = st.radio(
        "PPP Valuation Framework:",
        [
            "Institutional Decomposed (GFCF + Global Revenue Split)",
            "Standard Consumer Parity (World Bank ICP)",
        ],
        index=0,
        help="Institutional Decomposed addresses capital goods tradability (GFCF) and multinational revenue splits. Standard Consumer Parity uses pure consumer basket factors."
    )
    is_decomposed = "Institutional Decomposed" in valuation_model and "net_worth_decomposed_ppp" in df.columns
    active_ppp_col = "net_worth_decomposed_ppp" if is_decomposed else "net_worth_ppp"
    active_uplift_col = "decomposed_uplift_pct" if is_decomposed else "ppp_uplift_pct"
    active_rank_ppp_col = "rank_decomposed_ppp" if is_decomposed else "rank_ppp"
    active_rank_change_col = "rank_change_decomposed" if is_decomposed else "rank_change"
    active_label_suffix = "Decomposed Int$" if is_decomposed else "Int$"

    # Cohort Size Slider
    top_n = st.slider("Cohort Size (Top N)", min_value=5, max_value=len(df), value=20, step=5)
    
    # Sort Selector
    sort_options = {
        "net_worth_usd": "Nominal Net Worth ($ USD)",
        active_ppp_col: f"Real PPP Net Worth ({active_label_suffix})",
        active_uplift_col: "Purchasing Power Uplift (%)",
        active_rank_change_col: "Rank Position Shift (ΔR)",
    }
    sort_by = st.selectbox(
        "Sort Cohort By:",
        options=list(sort_options.keys()),
        format_func=lambda k: sort_options[k],
        index=0,
    )
    
    # Multi-Country Filter
    all_countries = sorted(df["country"].unique())
    selected_countries = st.multiselect(
        "Filter by Country:",
        options=all_countries,
        default=[],
        help="Filter the billionaire ledger to specific sovereign economies."
    )
    
    # Minimum Wealth Slider
    min_wealth = st.slider(
        "Min Nominal Wealth ($B):",
        min_value=float(df["net_worth_usd"].min()),
        max_value=float(df["net_worth_usd"].max()),
        value=float(df["net_worth_usd"].min()),
        step=5.0,
    )

    st.markdown("---")
    st.markdown("#### 📚 Metadata")
    st.caption(f"**Baseline Date:** {config.get('analysis_date', 'Jan 2026')}")
    st.caption(f"**Wealth Source:** {config.get('data_source', 'Forbes RT')}")
    st.caption(f"**PPP Indicator:** {config.get('ppp_source', 'World Bank WDI')}")
    st.markdown("---")
    st.caption("Built with Streamlit, Plotly & Scikit-Learn")


# Filter Dataset
filtered_df = df.copy()
if selected_countries:
    filtered_df = filtered_df[filtered_df["country"].isin(selected_countries)]
filtered_df = filtered_df[filtered_df["net_worth_usd"] >= min_wealth]

if filtered_df.empty:
    st.warning("No individuals match the current filter criteria. Please broaden your selection.")
    st.stop()


# ──────────────────────────────────────────────────────────────────────────────
# 4. HERO SECTION & EXECUTIVE METRICS RIBBON
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-badge">Macroeconomic Analytics & ML Wealth Engine</div>', unsafe_html=True)
st.markdown('<div class="hero-title">Global Billionaire Wealth: Nominal vs. Purchasing Power Parity</div>', unsafe_html=True)
st.markdown(
    '<div class="hero-subtitle">Evaluating sovereign purchasing power, domestic resource command, and currency friction for the world’s wealthiest individuals.</div>',
    unsafe_html=True
)

with st.expander("ℹ️ Theoretical Framework & Mathematical Formulation", expanded=False):
    st.markdown("""
    Standard wealth rankings measure net worth exclusively in nominal USD at spot market exchange rates ($W_{\\text{USD}}$). 
    However, domestic goods, physical labor, services, and fixed capital in emerging markets trade at significant structural discounts.
    
    $$\\text{Real Domestic Purchasing Power (Int\\$)} = W_{\\text{USD}} \\times \\left( \\frac{\\text{Exchange Rate (LCU/USD)}}{\\text{World Bank PPP Factor (LCU/Int\\$)}} \\right)$$
    
    * **PPP Multiplier ($\\mu$):** $\\frac{\\text{FX Rate}}{\\text{PPP Factor}}$. If $\\mu > 1$, local prices are lower than US parity, multiplying domestic resource power.
    * **Rank Displacement ($\\Delta R$):** $R_{\\text{Nominal}} - R_{\\text{PPP}}$. Positive values indicate higher domestic standing than raw USD indicates.
    """)

# KPI Metric Cards
total_nom = filtered_df["net_worth_usd"].sum()
total_ppp = filtered_df[active_ppp_col].sum()
net_expansion = total_ppp - total_nom
expansion_pct = (net_expansion / total_nom) * 100 if total_nom > 0 else 0

top_mover = filtered_df.nlargest(1, active_rank_change_col).iloc[0] if active_rank_change_col in filtered_df.columns else None

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(
    label="Total Nominal Wealth",
    value=f"${total_nom:,.1f}B",
    help="Combined market exchange net worth in USD."
)
kpi2.metric(
    label=f"Total Real PPP Wealth ({active_label_suffix})",
    value=f"${total_ppp:,.1f}B",
    delta=f"+${net_expansion:,.1f}B Real Gain",
    help=f"Adjusted via {valuation_model}."
)
kpi3.metric(
    label="Cohort Net Expansion",
    value=f"+{expansion_pct:.1f}%",
    delta=f"{filtered_df[active_uplift_col].median():.1f}% Median Uplift",
    help="Aggregate percentage gain in real purchasing power across cohort."
)
if top_mover is not None:
    kpi4.metric(
        label="Top Rank Gainer",
        value=f"{top_mover['name']}",
        delta=f"+{int(top_mover[active_rank_change_col])} Positions (to #{int(top_mover[active_rank_ppp_col])})",
        help=f"Highest upward rank displacement under {valuation_model}."
    )
else:
    kpi4.metric(label="Top Rank Gainer", value="N/A", delta="0")

st.markdown("<br>", unsafe_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 5. CORE BI APPLICATION TABS
# ──────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Market Overview",
    "📈 Analytical Deep Dive",
    "🌐 Geographic Dispersion",
    "🤖 ML Archetypes",
    "🔬 Macro Volatility & Risk",
    "📋 Analytical Ledger",
])

COLOR_NOMINAL = "#38BDF8"   # Electric Sky Blue
COLOR_PPP = "#F43F5E"       # Radiant Rose Crimson
PLOT_TEMPLATE = "plotly_dark"


# ── TAB 1: MARKET OVERVIEW ───────────────────────────────────────────────────
with tab1:
    col_lead, col_chart = st.columns([1, 2.5])
    
    with col_lead:
        st.subheader("Cohort Parameters")
        st.markdown(f"Displaying top **{min(top_n, len(filtered_df))}** billionaires sorted by **{sort_options[sort_by]}**.")
        st.info(f"💡 **Active Model:** {valuation_model}.")
        
        # Quick distribution metrics
        top_cohort = filtered_df.nlargest(top_n, sort_by)
        avg_top_nom = top_cohort["net_worth_usd"].mean()
        avg_top_ppp = top_cohort[active_ppp_col].mean()
        st.metric("Avg Cohort Nominal", f"${avg_top_nom:.1f}B")
        st.metric(f"Avg Cohort PPP ({active_label_suffix})", f"${avg_top_ppp:.1f}B")

    with col_chart:
        cohort_plot = filtered_df.nlargest(top_n, sort_by).copy()
        
        fig_bars = go.Figure()
        fig_bars.add_trace(go.Bar(
            y=cohort_plot["name"],
            x=cohort_plot["net_worth_usd"],
            name="Nominal USD ($B)",
            orientation="h",
            marker=dict(color=COLOR_NOMINAL, line=dict(color="rgba(255,255,255,0.2)", width=1)),
            hovertemplate="<b>%{y}</b><br>Nominal Wealth: $%{x:,.1f}B<extra></extra>"
        ))
        fig_bars.add_trace(go.Bar(
            y=cohort_plot["name"],
            x=cohort_plot[active_ppp_col],
            name=f"Real PPP Wealth ({active_label_suffix} B)",
            orientation="h",
            marker=dict(color=COLOR_PPP, line=dict(color="rgba(255,255,255,0.2)", width=1)),
            hovertemplate=f"<b>%{{y}}</b><br>Real PPP Wealth: $%{{x:,.1f}}B {active_label_suffix}<extra></extra>"
        ))
        fig_bars.update_layout(
            barmode="group",
            height=max(450, len(cohort_plot) * 26),
            yaxis=dict(autorange="reversed", title=None),
            xaxis=dict(title="Wealth Valuation ($ Billions)", gridcolor="rgba(255,255,255,0.08)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            template=PLOT_TEMPLATE,
            margin=dict(l=160, r=20, t=30, b=40),
        )
        st.plotly_chart(fig_bars, use_container_width=True)

    st.markdown("---")
    st.subheader("Parity Divergence Scatter Plot")
    st.caption("Points above the dashed 1:1 diagonal line reflect domestic purchasing power expansion (PPP Uplift > 0%).")
    
    fig_scatter = px.scatter(
        filtered_df,
        x="net_worth_usd",
        y=active_ppp_col,
        color="country",
        size="net_worth_usd",
        hover_name="name",
        hover_data=["rank", active_rank_ppp_col, active_rank_change_col, active_uplift_col],
        labels={
            "net_worth_usd": "Nominal Net Worth ($B USD)",
            active_ppp_col: f"Real PPP Net Worth ($B {active_label_suffix})",
            "country": "Sovereign State",
            active_uplift_col: "PPP Uplift (%)"
        },
        template=PLOT_TEMPLATE,
        height=550,
    )
    max_axis = max(filtered_df["net_worth_usd"].max(), filtered_df[active_ppp_col].max()) * 1.08
    fig_scatter.add_trace(go.Scatter(
        x=[0, max_axis],
        y=[0, max_axis],
        mode="lines",
        line=dict(dash="dash", color="rgba(255,255,255,0.4)", width=1.5),
        name="Parity Baseline (1:1)",
        hoverinfo="skip"
    ))
    st.plotly_chart(fig_scatter, use_container_width=True)


# ── TAB 2: ANALYTICAL DEEP DIVE ──────────────────────────────────────────────
with tab2:
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        st.subheader("Top Purchasing Power Gains (%)")
        st.caption(f"Percentage boost in real domestic capital power under {valuation_model}.")
        
        top_uplift = filtered_df.nlargest(15, active_uplift_col)
        fig_uplift = px.bar(
            top_uplift,
            x=active_uplift_col,
            y="name",
            orientation="h",
            color=active_uplift_col,
            color_continuous_scale="Tealrose",
            labels={active_uplift_col: "Purchasing Power Uplift (%)", "name": ""},
            hover_data=["country", "net_worth_usd", active_ppp_col],
            template=PLOT_TEMPLATE,
            height=max(450, len(top_uplift) * 26),
        )
        fig_uplift.update_layout(
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False,
            margin=dict(l=160, r=20, t=30, b=40)
        )
        fig_uplift.update_traces(texttemplate='%{x:.0f}%', textposition='outside')
        st.plotly_chart(fig_uplift, use_container_width=True)

    with col_d2:
        st.subheader("Global Rank Displacement Ladder")
        st.caption(f"Positions gained (green) or compressed (muted) when evaluating through {valuation_model}.")
        
        movers_df = filtered_df.loc[filtered_df[active_rank_change_col].abs().sort_values(ascending=False).index[:15]]
        fig_disp = px.bar(
            movers_df.sort_values(active_rank_change_col, ascending=True),
            x=active_rank_change_col,
            y="name",
            orientation="h",
            color=active_rank_change_col,
            color_continuous_scale="Blues",
            labels={active_rank_change_col: "Rank Positions Displaced (ΔR)", "name": ""},
            hover_data=["country", "rank", active_rank_ppp_col],
            template=PLOT_TEMPLATE,
            height=max(450, len(movers_df) * 26),
        )
        fig_disp.update_layout(coloraxis_showscale=False, margin=dict(l=160, r=20, t=30, b=40))
        fig_disp.update_traces(texttemplate='%{x:+}', textposition='outside')
        st.plotly_chart(fig_disp, use_container_width=True)


# ── TAB 3: GLOBAL GEOGRAPHIC IMPACT & MAP ────────────────────────────────────
with tab3:
    st.subheader("🌐 Global Purchasing Power Parity Multiplier by Country")
    st.caption("Choropleth mapping sovereign purchasing power expansion factors (FX / PPP).")
    
    country_summary = filtered_df.groupby(["country", "iso_alpha"]).agg(
        avg_uplift=("ppp_uplift_pct", "mean"),
        avg_multiplier=("fx_rate", lambda fx: (fx / filtered_df.loc[fx.index, "ppp_factor"]).mean()),
        total_nominal=("net_worth_usd", "sum"),
        total_ppp=("net_worth_ppp", "sum"),
        billionaire_count=("name", "count")
    ).reset_index()

    fig_map = px.choropleth(
        country_summary,
        locations="iso_alpha",
        color="avg_uplift",
        hover_name="country",
        hover_data={
            "iso_alpha": False,
            "avg_uplift": ":.1f",
            "billionaire_count": True,
            "total_ppp": ":$,.1f"
        },
        color_continuous_scale="Viridis",
        labels={"avg_uplift": "Average Uplift (%)", "total_ppp": "Total PPP ($B)"},
        template=PLOT_TEMPLATE,
        height=520,
    )
    fig_map.update_geos(
        showcoastlines=True,
        coastlinecolor="rgba(255,255,255,0.15)",
        showland=True,
        landcolor="rgba(30,41,59,0.5)",
        showocean=True,
        oceancolor="rgba(15,23,42,0.8)",
        projection_type="natural earth"
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=10))
    st.plotly_chart(fig_map, use_container_width=True)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Average PPP Uplift by Nation")
        fig_country_bar = px.bar(
            country_summary.sort_values("avg_uplift", ascending=False),
            x="country",
            y="avg_uplift",
            text="avg_uplift",
            color="avg_uplift",
            color_continuous_scale="Viridis",
            labels={"avg_uplift": "Avg Uplift (%)", "country": "Country"},
            template=PLOT_TEMPLATE,
            height=380,
        )
        fig_country_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_country_bar.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=20, t=10, b=20))
        st.plotly_chart(fig_country_bar, use_container_width=True)

    with col_g2:
        st.subheader("Global PPP Wealth Share")
        fig_donut = px.pie(
            country_summary,
            values="total_ppp",
            names="country",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Bold,
            template=PLOT_TEMPLATE,
            height=380,
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent+label")
        fig_donut.update_layout(margin=dict(l=0, r=0, t=10, b=20), showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True)


# ── TAB 4: ML WEALTH ARCHETYPES ──────────────────────────────────────────────
with tab4:
    st.subheader("🤖 Unsupervised Machine Learning: UHNWI Wealth Archetypes")
    st.markdown("Segment billionaires into macroeconomic wealth structures via unsupervised clustering.")

    ml_algorithm = st.radio(
        "Clustering Algorithm:",
        [
            "Bayesian Gaussian Mixture Models (Soft Probabilistic Archetypes)",
            "Standard K-Means (Hard Clusters)",
        ],
        horizontal=True,
        help="Gaussian Mixture Models calculate posterior probabilities and entropy uncertainty for boundary individuals. K-Means assigns hard discrete clusters."
    )

    use_gmm = "Gaussian Mixture" in ml_algorithm and segment_billionaires_gmm is not None

    if segment_billionaires is not None:
        try:
            if use_gmm:
                clustered_df = segment_billionaires_gmm(filtered_df)
                label_col = "gmm_label"
                bic_val = clustered_df.attrs.get("gmm_bic", "N/A")
                st.info(f"📊 **Bayesian Model Fit:** BIC = `{bic_val}` | Average Assignment Confidence = `{clustered_df['gmm_max_prob'].mean() * 100:.1f}%`")
            else:
                clustered_df = segment_billionaires(filtered_df)
                label_col = "archetype_label"
            
            # Archetype metrics overview
            c_metrics = clustered_df.groupby(label_col).agg(
                count=("name", "count"),
                avg_nominal=("net_worth_usd", "mean"),
                avg_ppp=(active_ppp_col, "mean"),
                avg_uplift=(active_uplift_col, "mean"),
            ).reset_index()

            col_m1, col_m2, col_m3 = st.columns(3)
            for idx, row in c_metrics.iterrows():
                target_col = [col_m1, col_m2, col_m3][idx % 3]
                target_col.metric(
                    label=row[label_col],
                    value=f"{row['count']} Individuals",
                    delta=f"${row['avg_nominal']:.1f}B Nom → ${row['avg_ppp']:.1f}B {active_label_suffix}"
                )

            st.markdown("<br>", unsafe_allow_html=True)

            hover_cols = ["country", "net_worth_usd", active_ppp_col, active_uplift_col]
            if use_gmm and "gmm_max_prob" in clustered_df.columns:
                hover_cols.extend(["gmm_max_prob", "gmm_ambiguity"])

            fig_ml = px.scatter(
                clustered_df,
                x="net_worth_usd",
                y=active_ppp_col,
                color=label_col,
                size="net_worth_usd",
                hover_name="name",
                hover_data=hover_cols,
                labels={
                    "net_worth_usd": "Nominal Net Worth ($B USD)",
                    active_ppp_col: f"Real PPP Net Worth ($B {active_label_suffix})",
                    label_col: "Identified Archetype",
                    active_uplift_col: "PPP Uplift (%)",
                    "gmm_max_prob": "Classification Certainty",
                    "gmm_ambiguity": "Entropy Ambiguity"
                },
                color_discrete_sequence=["#38BDF8", "#F59E0B", "#10B981"],
                template=PLOT_TEMPLATE,
                height=520,
            )
            st.plotly_chart(fig_ml, use_container_width=True)

            if use_gmm and "gmm_ambiguity" in clustered_df.columns:
                st.markdown("---")
                st.subheader("🌫️ Boundary Uncertainty & Hybrid Archetype Titans")
                st.caption("Individuals with elevated Shannon entropy straddle the boundary between emerging market leverage and global liquidity.")
                
                ambiguous = clustered_df.nlargest(5, "gmm_ambiguity")[
                    ["name", "country", "net_worth_usd", active_ppp_col, "gmm_label", "gmm_max_prob", "gmm_ambiguity"]
                ]
                st.dataframe(ambiguous, use_container_width=True)

        except Exception as e:
            st.warning(f"Could not compute clustering on current subset: {e}")
    else:
        st.info("Clustering engine module loading...")


# ── TAB 5: MACRO SENSITIVITY & FX SHOCKS ─────────────────────────────────────
with tab5:
    st.subheader("🔬 Macroeconomic FX Rate Volatility & Stress Testing")
    st.markdown("Simulate how currency depreciation or appreciation reconfigures global purchasing power rankings.")

    col_sim_ctrl, col_sim_view = st.columns([1, 2])
    
    with col_sim_ctrl:
        st.markdown("**Simulation Settings**")
        scenario_preset = st.radio(
            "Quick Scenarios:",
            ["Standard Volatility (±10%)", "Emerging Market FX Shock (+20%)", "Global Dollar Slump (-15%)", "Custom"],
            index=0
        )
        if scenario_preset == "Standard Volatility (±10%)":
            fx_shift_val = 10
        elif scenario_preset == "Emerging Market FX Shock (+20%)":
            fx_shift_val = 20
        elif scenario_preset == "Global Dollar Slump (-15%)":
            fx_shift_val = 15
        else:
            fx_shift_val = st.slider("Custom FX Rate Shift (%):", min_value=5, max_value=35, value=10, step=5)

        shift_frac = fx_shift_val / 100.0

    # Sensitivity calculation
    sens_calc = filtered_df.copy()
    sens_calc["ppp_base"] = sens_calc["net_worth_usd"] * (sens_calc["fx_rate"] / sens_calc["ppp_factor"])
    sens_calc["ppp_weaker"] = sens_calc["net_worth_usd"] * ((sens_calc["fx_rate"] * (1 + shift_frac)) / sens_calc["ppp_factor"])
    sens_calc["ppp_stronger"] = sens_calc["net_worth_usd"] * ((sens_calc["fx_rate"] * (1 - shift_frac)) / sens_calc["ppp_factor"])
    
    sens_calc["rank_base"] = sens_calc["ppp_base"].rank(ascending=False, method="min").astype(int)
    sens_calc["rank_weaker"] = sens_calc["ppp_weaker"].rank(ascending=False, method="min").astype(int)
    sens_calc["rank_stronger"] = sens_calc["ppp_stronger"].rank(ascending=False, method="min").astype(int)
    sens_calc["rank_volatility"] = (sens_calc[["rank_weaker", "rank_stronger"]].max(axis=1) - 
                                     sens_calc[["rank_weaker", "rank_stronger"]].min(axis=1))

    with col_sim_view:
        st.markdown(f"**Rank Volatility Impact (±{fx_shift_val}% Shift)**")
        top_volatile = sens_calc.nlargest(10, "rank_volatility")
        fig_vol_bar = px.bar(
            top_volatile,
            x="rank_volatility",
            y="name",
            orientation="h",
            color="country",
            labels={"rank_volatility": "Positions Swung (Volatility)", "name": ""},
            template=PLOT_TEMPLATE,
            height=max(450, len(top_volatile) * 26),
        )
        fig_vol_bar.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=160, r=20, t=30, b=40))
        st.plotly_chart(fig_vol_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("🎲 Stochastic Monte Carlo FX Risk Engine (500 Correlated Paths)")
    st.caption("Simulates joint sovereign foreign exchange shocks to calculate Value-at-Risk (95% VaR) and Expected Shortfall of rank displacements.")
    
    if monte_carlo_fx_simulation is not None and len(filtered_df) >= 3:
        mc_results = monte_carlo_fx_simulation(filtered_df, n_simulations=500, random_state=42)
        
        mc_col1, mc_col2, mc_col3 = st.columns(3)
        mc_col1.metric("Average Rank Volatility", f"±{mc_results['sim_rank_std'].mean():.1f} Spots")
        mc_col2.metric("Maximum 95% VaR Rank Drop", f"{int(mc_results['rank_var_95'].max())} Spots")
        mc_col3.metric("Worst-Tail Expected Shortfall (CVaR)", f"{mc_results['rank_cvar_95'].max():.1f} Spots")
        
        st.markdown("<br>", unsafe_allow_html=True)
        top_risk = mc_results.nlargest(12, "rank_var_95").sort_values("rank_var_95", ascending=True)
        
        fig_mc = go.Figure()
        fig_mc.add_trace(go.Bar(
            y=top_risk["name"],
            x=top_risk["sim_rank_p95"] - top_risk["sim_rank_p05"],
            base=top_risk["sim_rank_p05"],
            orientation="h",
            name="90% Empirical Rank Range [P05, P95]",
            marker=dict(color="rgba(56, 189, 248, 0.35)", line=dict(color="#38BDF8", width=1.5)),
            hovertemplate="<b>%{y}</b><br>Empirical Range: #%{base} to #%{x}<extra></extra>"
        ))
        fig_mc.add_trace(go.Scatter(
            y=top_risk["name"],
            x=top_risk["base_ppp_rank"],
            mode="markers",
            name="Baseline Real Rank",
            marker=dict(color="#F43F5E", size=10, symbol="diamond"),
            hovertemplate="<b>%{y}</b><br>Baseline Rank: #%{x}<extra></extra>"
        ))
        fig_mc.update_layout(
            title="Stochastic Rank Dispersion & Vulnerability (Top VaR Exposures)",
            xaxis=dict(title="Simulated Global Rank Position (Lower = Richer)", autorange="reversed"),
            template=PLOT_TEMPLATE,
            height=max(450, len(top_risk) * 32),
            margin=dict(l=160, r=20, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_mc, use_container_width=True)


# ── TAB 6: MASTER DATA EXPLORER ──────────────────────────────────────────────
with tab6:
    st.subheader("📋 Comprehensive Analytical Ledger")
    
    search_query = st.text_input("🔍 Quick Search Individual or Sovereign State:", placeholder="Type name (e.g. Ambani, Musk) or country...")
    
    table_view = filtered_df.copy()
    if search_query:
        table_view = table_view[
            table_view["name"].str.contains(search_query, case=False, na=False) |
            table_view["country"].str.contains(search_query, case=False, na=False)
        ]

    cols_to_show = ["rank", "name", "country", "net_worth_usd", active_ppp_col, active_uplift_col, active_rank_ppp_col, active_rank_change_col]
    if "domestic_share" in table_view.columns:
        cols_to_show.append("domestic_share")
    cols_to_show = [c for c in cols_to_show if c in table_view.columns]

    st.dataframe(
        table_view[cols_to_show],
        column_config={
            "rank": st.column_config.NumberColumn("Nominal Rank", format="#%d"),
            "name": st.column_config.TextColumn("Billionaire Entity", width="medium"),
            "country": st.column_config.TextColumn("Country"),
            "net_worth_usd": st.column_config.NumberColumn("Nominal ($B)", format="$%.1fB"),
            active_ppp_col: st.column_config.NumberColumn(f"Real PPP ({active_label_suffix})", format="$%.1fB"),
            active_uplift_col: st.column_config.ProgressColumn("PPP Uplift (%)", min_value=0, max_value=350, format="+%.1f%%"),
            active_rank_ppp_col: st.column_config.NumberColumn("PPP Rank", format="#%d"),
            active_rank_change_col: st.column_config.NumberColumn("Position Delta (ΔR)", format="%+d"),
            "domestic_share": st.column_config.NumberColumn("Domestic Share", format="%.0%%"),
        },
        use_container_width=True,
        hide_index=True,
        height=550,
    )

    csv_data = table_view[cols_to_show].to_csv(index=False)
    st.download_button(
        label="⬇️ Export Master Dataset (CSV)",
        data=csv_data,
        file_name="realrich_ppp_master.csv",
        mime="text/csv",
    )


# ──────────────────────────────────────────────────────────────────────────────
# 6. ENTERPRISE CITATIONS & FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div class="footer-text">RealRich PPP Analytics Platform v2.0 • Data Sources: Forbes Real-Time Index & World Bank WDI (ICP) • Distributed under MIT License</div>',
    unsafe_allow_html=True
)
