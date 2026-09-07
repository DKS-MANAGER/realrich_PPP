import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# ──────────────────────────────────────────────────────────────────────────────
# 1. PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Billionaire Wealth: Nominal vs PPP",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark premium theme
st.markdown("""
<style>
    .block-container { padding-top: 2rem !important; }
    div[data-testid="stMetric"] {
        background-color: #262730; border: 1px solid #41444e;
        padding: 15px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetric"] label { color: #aeb5bc; }
    div[data-testid="stTabs"] button { font-size: 1.05rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 2. DATA LOADING
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    """Load and prepare the PPP-adjusted dataset."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Prioritize master processed dataset, with local dashboard fallback
    candidates = [
        "data/processed/top50_nominal_and_ppp.csv",
        "data/output/top50_nominal_and_ppp.csv",
        os.path.join(base_path, "data", "richest_ppp.csv"),
        os.path.join("dashboard", "data", "richest_ppp.csv"),
        os.path.join("wealth_dashboard", "data", "richest_ppp.csv"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            df = pd.read_csv(candidate)
            break
    else:
        st.error("Data file not found. Please ensure data is available.")
        return None

    # Normalize column names
    col_map = {
        "net_worth_PPP_intl$": "net_worth_ppp",
        "net_worth_USD": "net_worth_usd",
        "percent_difference_vs_nominal_USD": "ppp_uplift_pct",
        "rank_nominal": "rank",
        "primary_country": "country",
        "name": "name",
        "PPP_conversion_factor": "ppp_factor",
        "exchange_rate_local_per_USD": "fx_rate",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # Derived columns
    if "ppp_uplift_pct" not in df.columns and "net_worth_ppp" in df.columns:
        df["ppp_uplift_pct"] = (
            (df["net_worth_ppp"] - df["net_worth_usd"]) / df["net_worth_usd"] * 100
        ).round(1)
    if "rank" in df.columns:
        df["rank"] = df["rank"].astype(int)

    # Compute PPP-adjusted rank
    if "net_worth_ppp" in df.columns:
        df["rank_ppp"] = df["net_worth_ppp"].rank(ascending=False, method="min").astype(int)
        df["rank_change"] = df["rank"] - df["rank_ppp"]

    return df


@st.cache_data
def load_config():
    """Load PPP rates from config JSON."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    for candidate in [
        os.path.join(base_path, "..", "configs", "ppp_rates.json"),
        "configs/ppp_rates.json",
    ]:
        if os.path.exists(candidate):
            with open(candidate) as f:
                return json.load(f)
    return None


# ──────────────────────────────────────────────────────────────────────────────
# 3. SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
df = load_data()
config = load_config()

if df is None:
    st.stop()

st.sidebar.title("💰 RealRich PPP")
st.sidebar.markdown("Analyze billionaire wealth through the lens of **Purchasing Power Parity**.")
st.sidebar.divider()

# Filters
top_n = st.sidebar.slider("Show Top N", 5, 50, 20, step=5)
sort_by = st.sidebar.selectbox("Sort by", ["net_worth_usd", "net_worth_ppp", "ppp_uplift_pct"], index=0)
sort_labels = {
    "net_worth_usd": "Nominal USD",
    "net_worth_ppp": "PPP-Adjusted",
    "ppp_uplift_pct": "PPP Uplift %",
}
sort_label = sort_labels.get(sort_by, sort_by)

country_filter = st.sidebar.multiselect(
    "Filter by Country",
    options=sorted(df["country"].unique()) if "country" in df.columns else [],
    default=[],
)

st.sidebar.divider()
st.sidebar.caption(f"Data: {config['analysis_date'] if config else 'Jan 2026'}")
st.sidebar.caption(f"Source: {config['data_source'] if config else 'Forbes'}")


# ──────────────────────────────────────────────────────────────────────────────
# 4. MAIN CONTENT
# ──────────────────────────────────────────────────────────────────────────────
st.title("💰 Global Billionaire Wealth: Nominal vs PPP")
st.markdown(
    "*How does purchasing power parity change who the \"real\" wealthiest people are?*"
)

# ── KPI Row ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
filtered = df.copy()
if country_filter:
    filtered = filtered[filtered["country"].isin(country_filter)]

col1.metric("Total Nominal Wealth", f"${filtered['net_worth_usd'].sum():,.0f}B")
col2.metric("Total PPP Wealth", f"${filtered['net_worth_ppp'].sum():,.0f}B")
col3.metric("Avg PPP Uplift", f"{filtered['ppp_uplift_pct'].mean():.1f}%")
top_rank_change = filtered.nlargest(1, "rank_change") if "rank_change" in filtered.columns else None
if top_rank_change is not None and len(top_rank_change) > 0:
    col4.metric("Biggest Rank Mover", top_rank_change.iloc[0].get("name", "N/A"),
                f"↑ {int(top_rank_change.iloc[0].get('rank_change', 0))} positions")
else:
    col4.metric("Individuals", str(len(filtered)))

st.divider()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Overview", "📈 Analytical Deep Dive",
    "🌍 Geographic Impact", "🔬 Sensitivity Analysis", "📋 Data Explorer",
])

# ── Tab 1: Market Overview ───────────────────────────────────────────────────
with tab1:
    st.subheader(f"Top {top_n}: Nominal vs PPP Wealth")

    display_df = filtered.nlargest(top_n, sort_by).copy()

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Nominal USD", y=display_df["name"], x=display_df["net_worth_usd"],
        orientation="h", marker_color="#636EFA",
        hovertemplate="<b>%{y}</b><br>Nominal: $%{x:.1f}B<extra></extra>",
    ))
    fig_bar.add_trace(go.Bar(
        name="PPP-Adjusted", y=display_df["name"], x=display_df["net_worth_ppp"],
        orientation="h", marker_color="#EF553B",
        hovertemplate="<b>%{y}</b><br>PPP: $%{x:.1f}B<extra></extra>",
    ))
    fig_bar.update_layout(
        barmode="group", height=max(400, top_n * 30),
        yaxis=dict(autorange="reversed"), legend=dict(orientation="h", yanchor="bottom", y=1.02),
        template="plotly_dark", margin=dict(l=0, r=20, t=30, b=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Scatter: Nominal vs PPP with 1:1 line
    st.subheader("Correlation: Nominal vs PPP Wealth")
    fig_scatter = px.scatter(
        filtered, x="net_worth_usd", y="net_worth_ppp",
        color="country", size="net_worth_usd",
        hover_data=["name", "ppp_uplift_pct"],
        labels={"net_worth_usd": "Nominal USD ($B)", "net_worth_ppp": "PPP-Adjusted ($B)"},
        template="plotly_dark",
    )
    max_val = max(filtered["net_worth_usd"].max(), filtered["net_worth_ppp"].max()) * 1.1
    fig_scatter.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val], mode="lines",
        line=dict(dash="dash", color="white", width=1), name="1:1 Line",
        hoverinfo="skip",
    ))
    st.plotly_chart(fig_scatter, use_container_width=True)


# ── Tab 2: Analytical Deep Dive ──────────────────────────────────────────────
with tab2:
    st.subheader("PPP Uplift by Individual")

    uplift_df = filtered.nlargest(top_n, "ppp_uplift_pct").copy()
    fig_uplift = px.bar(
        uplift_df, x="ppp_uplift_pct", y="name", color="country",
        orientation="h",
        labels={"ppp_uplift_pct": "PPP Uplift (%)", "name": ""},
        hover_data=["net_worth_usd", "net_worth_ppp"],
        template="plotly_dark",
    )
    fig_uplift.update_layout(yaxis=dict(autorange="reversed"), height=max(400, top_n * 30),
                             margin=dict(l=0, r=20, t=30, b=20))
    st.plotly_chart(fig_uplift, use_container_width=True)

    st.subheader("Rank Movers: Biggest Position Changes")
    movers = filtered.nlargest(15, "rank_change") if "rank_change" in filtered.columns else pd.DataFrame()
    if not movers.empty:
        fig_movers = go.Figure()
        fig_movers.add_trace(go.Bar(
            name="Nominal Rank", y=movers["name"], x=movers["rank"],
            orientation="h", marker_color="#636EFA",
            hovertemplate="<b>%{y}</b><br>Nominal Rank: %{x}<extra></extra>",
        ))
        fig_movers.add_trace(go.Bar(
            name="PPP Rank", y=movers["name"], x=movers["rank_ppp"],
            orientation="h", marker_color="#00CC96",
            hovertemplate="<b>%{y}</b><br>PPP Rank: %{x}<extra></extra>",
        ))
        fig_movers.update_layout(
            barmode="group", height=max(400, len(movers) * 30),
            yaxis=dict(autorange="reversed"), template="plotly_dark",
            margin=dict(l=0, r=20, t=30, b=20),
        )
        st.plotly_chart(fig_movers, use_container_width=True)


# ── Tab 3: Geographic Impact ─────────────────────────────────────────────────
with tab3:
    st.subheader("Country-Level Analysis")

    country_df = (
        filtered.groupby("country")
        .agg(
            avg_uplift=("ppp_uplift_pct", "mean"),
            total_nominal=("net_worth_usd", "sum"),
            total_ppp=("net_worth_ppp", "sum"),
            count=("name", "count"),
        )
        .reset_index()
        .sort_values("avg_uplift", ascending=False)
    )

    col_a, col_b = st.columns(2)
    with col_a:
        fig_avg = px.bar(
            country_df, x="avg_uplift", y="country", orientation="h",
            color="avg_uplift", color_continuous_scale="RdYlGn",
            labels={"avg_uplift": "Avg PPP Uplift (%)", "country": ""},
            template="plotly_dark",
        )
        fig_avg.update_layout(yaxis=dict(autorange="reversed"), height=500,
                              showlegend=False, margin=dict(l=0, r=20, t=10, b=20))
        st.plotly_chart(fig_avg, use_container_width=True)

    with col_b:
        fig_donut = px.pie(
            country_df, values="total_ppp", names="country",
            hole=0.4, template="plotly_dark",
            hover_data=["total_nominal", "count"],
            title="Total PPP Wealth Share by Country",
        )
        st.plotly_chart(fig_donut, use_container_width=True)


# ── Tab 4: Sensitivity Analysis ──────────────────────────────────────────────
with tab4:
    st.subheader("🔬 What-If: FX Rate Sensitivity")
    st.markdown("See how a shift in exchange rates affects PPP rankings.")

    fx_shift = st.slider(
        "FX Rate Shift (%)", min_value=5, max_value=30, value=10, step=5,
        help="Apply ±X% shift to all exchange rates and observe impact on rankings.",
    )
    shift_frac = fx_shift / 100.0

    # Compute sensitivity inline
    sens_df = filtered.copy()
    sens_df["ppp_base"] = sens_df["net_worth_usd"] * (
        sens_df["fx_rate"] / sens_df["ppp_factor"]
    )
    sens_df["ppp_weaker_fx"] = sens_df["net_worth_usd"] * (
        (sens_df["fx_rate"] * (1 + shift_frac)) / sens_df["ppp_factor"]
    )
    sens_df["ppp_stronger_fx"] = sens_df["net_worth_usd"] * (
        (sens_df["fx_rate"] * (1 - shift_frac)) / sens_df["ppp_factor"]
    )
    sens_df["rank_base"] = sens_df["ppp_base"].rank(ascending=False, method="min").astype(int)
    sens_df["rank_weaker"] = sens_df["ppp_weaker_fx"].rank(ascending=False, method="min").astype(int)
    sens_df["rank_stronger"] = sens_df["ppp_stronger_fx"].rank(ascending=False, method="min").astype(int)
    sens_df["rank_volatility"] = sens_df[["rank_weaker", "rank_stronger"]].max(axis=1) - \
        sens_df[["rank_weaker", "rank_stronger"]].min(axis=1)

    col_x, col_y = st.columns(2)
    with col_x:
        st.markdown(f"**Most Rank-Volatile (±{fx_shift}% FX shift)**")
        volatile = sens_df.nlargest(10, "rank_volatility")[
            ["name", "country", "rank_base", "rank_weaker", "rank_stronger", "rank_volatility"]
        ]
        st.dataframe(volatile, use_container_width=True, hide_index=True)

    with col_y:
        fig_vol = px.bar(
            sens_df.nlargest(10, "rank_volatility"),
            x="rank_volatility", y="name", orientation="h",
            color="country",
            labels={"rank_volatility": "Rank Positions Swung", "name": ""},
            template="plotly_dark",
            hover_data=["rank_base", "rank_weaker", "rank_stronger"],
        )
        fig_vol.update_layout(yaxis=dict(autorange="reversed"), height=400,
                              margin=dict(l=0, r=20, t=10, b=20))
        st.plotly_chart(fig_vol, use_container_width=True)


# ── Tab 5: Data Explorer ─────────────────────────────────────────────────────
with tab5:
    st.subheader("Full Dataset")

    display_cols = ["name", "country", "net_worth_usd", "net_worth_ppp",
                    "ppp_uplift_pct", "rank", "rank_ppp", "rank_change"]
    display_cols = [c for c in display_cols if c in filtered.columns]

    styled = filtered[display_cols].style
    if "rank_change" in display_cols:
        styled = styled.map(
            lambda v: "background-color: #1a472a" if isinstance(v, (int, float)) and v > 0
            else ("background-color: #4a1a1a" if isinstance(v, (int, float)) and v < 0 else ""),
            subset=["rank_change"],
        )

    st.dataframe(styled, use_container_width=True, hide_index=True, height=600)

    # Download
    csv = filtered[display_cols].to_csv(index=False)
    st.download_button("⬇️ Download CSV", csv, "ppp_analysis.csv", "text/csv")
