import streamlit as st
import pandas as pd
import plotly.express as px
import os
import datetime

# -----------------------------------------------------------------------------
# 1. VISUAL CONFIGURATION & PAGE SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Global Billionaire Wealth: Nominal vs PPP",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. ROBUST DATA LOADING & PROCESSING
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    """
    Loads, cleans, and pre-processes data.
    Ensures robustness, integer ranks, and centralized derivations.
    """
    # 2.1 Robust Path Handling
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, "data", "richest_ppp.csv")
    except NameError:
        file_path = "data/richest_ppp.csv"
        # Fallback search
        if not os.path.exists(file_path):
             potential_path = os.path.join("wealth_dashboard", "data", "richest_ppp.csv")
             if os.path.exists(potential_path):
                 file_path = potential_path

    if not os.path.exists(file_path):
        return None

    df = pd.read_csv(file_path)

    # 2.2 Rename fragility (A.1)
    # Map raw column names to clean, pythonic names
    col_map = {
        'net_worth_PPP_intl$': 'net_worth_ppp',
        'net_worth_USD': 'net_worth_usd',
        'percent_difference_vs_nominal_USD': 'ppp_uplift_pct'
    }
    df = df.rename(columns=col_map)
    
    # 2.3 Data Validation (A.4)
    # Ensure critical columns exist
    required_cols = ['name', 'primary_country', 'net_worth_usd', 'net_worth_ppp', 'rank_nominal']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"Data Integrity Error: Missing columns {missing}")
        st.stop()
        
    # Ensure no negative wealth
    if (df['net_worth_usd'] < 0).any():
        st.warning("Warning: Negative wealth values detected in nominal data.")

    # 2.4 Centralized Derivations (A.5)
    # Integer Ranks (A.2)
    df['rank_nominal'] = df['rank_nominal'].astype(int)
    df['ppp_rank'] = df['net_worth_ppp'].rank(ascending=False, method='min').astype(int)
    
    # Rank Change Semantics (A.3): Positive = Improvement (Moved Closer to #1)
    df['rank_change'] = (df['rank_nominal'] - df['ppp_rank']).astype(int)
    
    # PPP Ratio (F.21)
    df['ppp_ratio'] = df['net_worth_ppp'] / df['net_worth_usd']
    
    # Recalculate Uplift to be sure (B.8)
    df['ppp_uplift_pct'] = ((df['net_worth_ppp'] - df['net_worth_usd']) / df['net_worth_usd']) * 100
    
    return df

df = load_data()

if df is None:
    st.error("🚨 Critical Error: Data file not found. ensure 'data/richest_ppp.csv' exists.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. THEME & ASSETS
# -----------------------------------------------------------------------------
def load_css():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        css_path = os.path.join(base_dir, "assets", "theme.css")
    except NameError:
        css_path = "assets/theme.css"
        if not os.path.exists(css_path) and os.path.exists("wealth_dashboard/assets/theme.css"):
            css_path = "wealth_dashboard/assets/theme.css"
            
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# -----------------------------------------------------------------------------
# 4. SIDEBAR GLOBAL CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.title("Dashboard Controls")

# C.12 Filters (Visual Grouping)
with st.sidebar.container():
    st.sidebar.subheader("Filter Data")
    selected_countries = st.sidebar.multiselect(
        "Primary Country",
        options=sorted(df['primary_country'].unique()),
        default=[]
    )

    # UI Fix: Clearer Search
    search_name = st.sidebar.text_input("Search Individual", placeholder="Type a name...")

    min_rank_change = st.sidebar.number_input(
    "Min Rank Improvement", 
    min_value=0, 
    max_value=int(df['rank_change'].max()), 
    value=0,
    help="Filter for billionaires who gained at least this many spots in ranking."
)

# Apply Filters
df_filtered = df.copy()

if selected_countries:
    df_filtered = df_filtered[df_filtered['primary_country'].isin(selected_countries)]

if search_name:
    df_filtered = df_filtered[df_filtered['name'].str.contains(search_name, case=False)]

if min_rank_change > 0:
    df_filtered = df_filtered[df_filtered['rank_change'] >= min_rank_change]

# -----------------------------------------------------------------------------
# 5. HEADER & KPI SECTION (B.6)
# -----------------------------------------------------------------------------
st.title("Global Billionaire Wealth: Nominal vs PPP")

# UI Fix: Visible Methodology Summary
st.markdown("**Methodology:** *PPP-adjusted wealth reflects domestic purchasing power, not global spending power.*")

# E.17 Reduce Text Density
with st.expander("ℹ️ Click for Definitions", expanded=False):
    st.markdown("""
    **Purchasing Power Parity (PPP)** adjusts wealth to reflect what it can actually buy in the billionaire's home country.
    
    *   **Nominal USD:** Standard market exchange rates. Used for global asset comparison.
    *   **PPP Adjusted:** Adjusted for local cost of living (World Bank factors).
    *   **Rank Change:** Positive values (+5) indicate **improvement** in ranking (e.g., #10 → #5).
    *   **PPP Uplift:** Percentage increase in purchasing power derived from local cost advantages.
    """)

# KPI Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("👤 Individuals", f"{len(df_filtered)}")
with kpi2:
    st.metric("💰 Max Nominal", f"${df_filtered['net_worth_usd'].max():,.1f}B")
with kpi3:
    st.metric("📈 Max PPP", f"${df_filtered['net_worth_ppp'].max():,.1f}B")
with kpi4:
    # UI Fix: Better Stat for Median/Mean
    val = df_filtered['ppp_uplift_pct'].median()
    lbl = "Median Uplift"
    if abs(val) < 0.1:
         val = df_filtered['ppp_uplift_pct'].mean()
         lbl = "Mean Uplift"
    st.metric(f"📊 {lbl}", f"{val:+.1f}%", help="Typical purchasing power gain.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. MAIN CONTENT TABS (D.14, B.9)
# -----------------------------------------------------------------------------
tab_overview, tab_analysis, tab_explorer = st.tabs(["📊 Market Overview", "📈 Analytical Deep Dive", "🔢 Data Explorer"])

# --- TAB 1: OVERVIEW (Visual Clarity) ---
with tab_overview:
    # Top Section: Control and Chart
    col_ctrl, col_chart = st.columns([1, 3])
    
    with col_ctrl:
        # UI Fix: Container for Settings
        with st.container(border=True):
            st.subheader("View Settings")
            metric_mode = st.radio("Rank & Sort By:", ["Nominal USD", "PPP Adjusted"], index=0)
            show_top_n = st.slider("Show Top:", 5, 50, 10)
            
            st.info("💡 **Tip:** Notice how US billionaires dominate Nominal, but Emerging Markets rise in PPP.")

    with col_chart:
        # B.7 Consistent Color Semantics
        COLOR_NOMINAL = "#636EFA" # Purple/Blue
        COLOR_PPP = "#EF553B"     # Red/Orange

        sort_col = "net_worth_usd" if metric_mode == "Nominal USD" else "net_worth_ppp"
        df_plot = df_filtered.sort_values(sort_col, ascending=False).head(show_top_n)

        # Prepare for Grouped Bar (B.9)
        df_melt = df_plot.melt(
            id_vars=["name", "primary_country"],
            value_vars=["net_worth_usd", "net_worth_ppp"],
            var_name="Metric",
            value_name="Wealth"
        )
        df_melt["Metric Label"] = df_melt["Metric"].map({
            "net_worth_usd": "Nominal USD",
            "net_worth_ppp": "PPP Adjusted"
        })

        fig_main = px.bar(
            df_melt,
            x="Wealth",
            y="name",
            color="Metric Label",
            barmode="group",
            orientation="h",
            color_discrete_map={"Nominal USD": COLOR_NOMINAL, "PPP Adjusted": COLOR_PPP},
            height=500 + (show_top_n * 10),
            title=f"Top {show_top_n} Wealth Comparison"
        )
        fig_main.update_layout(
            yaxis={'categoryorder':'total ascending'},
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None),
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Net Worth ($ Billion)",
            yaxis_title=None
        )
        st.plotly_chart(fig_main, width="stretch", key="main_chart")
    
    # Scatter Plot (B.10 Annotations)
    st.subheader("Correlation Analysis", help="The diagonal line represents equal Nominal and PPP wealth. Points ABOVE the line indicate stronger local purchasing power.")
    st.caption("Diagonal Line = No PPP Effect (Factor 1.0). Points ABOVE the line have higher domestic purchasing power.")
    
    fig_scatter = px.scatter(
        df_filtered,
        x="net_worth_usd",
        y="net_worth_ppp",
        size="net_worth_usd",
        color="primary_country",
        hover_name="name",
        hover_data=["rank_nominal", "ppp_rank", "rank_change"],
        labels={"net_worth_usd": "Nominal Wealth ($B)", "net_worth_ppp": "PPP Wealth ($B)", "primary_country": "Country"},
        height=600
    )
    # Add Diagonal
    field_max = max(df_filtered['net_worth_usd'].max(), df_filtered['net_worth_ppp'].max()) * 1.05
    fig_scatter.add_shape(type="line", x0=0, y0=0, x1=field_max, y1=field_max, line=dict(color="Gray", width=1, dash="dot"))
    
    # Annotate Top Gainer
    top_gainer = df_filtered.loc[df_filtered['ppp_uplift_pct'].idxmax()]
    fig_scatter.add_annotation(
        x=top_gainer['net_worth_usd'], y=top_gainer['net_worth_ppp'],
        text=f"Max Uplift: {top_gainer['name']}",
        showarrow=True, arrowhead=1
    )
    
    fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_scatter, width="stretch", key="scatter_chart")

# --- TAB 2: ANALYTICAL DEEP DIVE ---
with tab_analysis:
    col1, col2 = st.columns(2)
    
    with col1:
        # B.8 PPP Uplift Bar Chart (Enhanced Color)
        st.subheader("Top Purchasing Power Gains", help="Billionaires whose wealth goes furthest in their home country.")
        st.caption("Percentage increase in wealth utility due to local prices.")
        
        df_uplifters = df_filtered.sort_values("ppp_uplift_pct", ascending=False).head(15)
        
        fig_uplift = px.bar(
            df_uplifters,
            x="ppp_uplift_pct",
            y="name",
            orientation="h",
            color="ppp_uplift_pct",
            # Green for positive impact, Red for negative (though rare in uplift contexts)
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            labels={"ppp_uplift_pct": "Uplift (%)", "name": ""}
        )
        fig_uplift.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
        fig_uplift.update_traces(texttemplate='%{x:.0f}%', textposition='outside')
        st.plotly_chart(fig_uplift, width="stretch", key="uplift_chart")
        
    with col2:
        # B.9 Rank Volatility
        st.subheader("Rank Movers", help="Difference between Nominal Rank and PPP Rank.")
        st.caption("Positive (Green) = Improved Rank. Negative (Red) = Dropped Rank.")
        
        df_movers = df_filtered.loc[df_filtered['rank_change'].abs().sort_values(ascending=False).index[:15]]
        
        fig_rank = px.bar(
            df_movers.sort_values("rank_change", ascending=True),
            x="rank_change",
            y="name",
            orientation="h",
            color="rank_change",
            color_continuous_scale="RdYlGn",
            # Color midpoint at 0
            range_color=[-20, 20],
            labels={"rank_change": "Rank Change", "name": ""}
        )
        fig_rank.update_layout(plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
        fig_rank.update_traces(texttemplate='%{x:+}', textposition='outside')
        st.plotly_chart(fig_rank, width="stretch", key="rank_chart")
        
    st.markdown("---")
    
    # F.22 Country Aggregation
    st.subheader("Geographic Impact Analysis")
    col_geo1, col_geo2 = st.columns(2)
    
    # Aggregation
    geo_agg = df_filtered.groupby("primary_country").agg({
        "net_worth_usd": "sum",
        "net_worth_ppp": "sum",
        "name": "count"
    }).reset_index()
    geo_agg["avg_uplift"] = ((geo_agg["net_worth_ppp"] - geo_agg["net_worth_usd"]) / geo_agg["net_worth_usd"]) * 100
    
    with col_geo1:
        st.markdown("**Average PPP Uplift by Country**")
        fig_geo = px.bar(
            geo_agg.sort_values("avg_uplift", ascending=False),
            x="primary_country",
            y="avg_uplift",
            text="avg_uplift",
            color="avg_uplift",
            color_continuous_scale="Magma",
            labels={"avg_uplift": "Avg PPP Uplift (%)", "primary_country": "Country"}
        )
        fig_geo.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_geo.update_layout(plot_bgcolor="rgba(0,0,0,0)", height=400, coloraxis_showscale=False)
        st.plotly_chart(fig_geo, key="geo_chart", width="stretch")
        
    with col_geo2:
        st.markdown("**Total Nominal Wealth Share**")
        fig_pie = px.pie(
            geo_agg,
            values="net_worth_usd",
            names="primary_country",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=False, height=400, margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, key="geo_pie_chart", width="stretch")
        
    # Insights Footer
    top_uplift = geo_agg.sort_values("avg_uplift", ascending=False).iloc[0]
    top_wealth = geo_agg.sort_values("net_worth_usd", ascending=False).iloc[0]
    st.info(f"💡 **Insight:** **{top_wealth['primary_country']}** holds the largest share of nominal wealth, whereas **{top_uplift['primary_country']}** sees the biggest PPP boost ({top_uplift['avg_uplift']:.1f}%).")

# --- TAB 3: DATA EXPLORER (C.11, C.13) ---
with tab_explorer:
    st.subheader("Detailed Records")
    
    # Configure Columns for Display
    display_df = df_filtered[[
        "rank_nominal", "name", "primary_country", 
        "net_worth_usd", "net_worth_ppp", "ppp_uplift_pct", 
        "ppp_rank", "rank_change"
    ]].sort_values("rank_nominal")
    
    # Conditional Formatting (Pandas Styler)
    # Green background for positive rank change, Red for negative
    # Gradient for PPP Impact
    def color_rank_change(val):
        """
        Takes a scalar and returns a string with
        the css property `'background-color: green'` if positive
        and `'background-color: red'` if negative.
        """
        if val > 0:
            return 'background-color: #d4edda; color: #155724' # Light Green
        elif val < 0:
            return 'background-color: #f8d7da; color: #721c24' # Light Red
        return ''

    styled_df = display_df.style.map(color_rank_change, subset=['rank_change'])\
                        .background_gradient(cmap='Greens', subset=['ppp_uplift_pct'])\
                        .format({
                            "net_worth_usd": "${:,.1f}B",
                            "net_worth_ppp": "${:,.1f}B",
                            "ppp_uplift_pct": "{:+.1f}%",
                            "rank_change": "{:+d}"
                        })

    st.dataframe(
        styled_df,
        column_config={
            "rank_nominal": st.column_config.NumberColumn("Nominal Rank", format="%d"),
            "name": st.column_config.TextColumn("Name", width="medium"),
            "primary_country": st.column_config.TextColumn("Country"),
            "net_worth_usd": st.column_config.NumberColumn("Nominal ($B)"),
            "net_worth_ppp": st.column_config.NumberColumn("PPP ($B)"),
            "ppp_uplift_pct": st.column_config.NumberColumn("Uplift"),
            "ppp_rank": st.column_config.NumberColumn("PPP Rank", format="%d"),
            "rank_change": st.column_config.NumberColumn("Rank Change"),
        },
        height=600,
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------------------------------------------------
# 7. FOOTER & DEPLOYMENT INFO (G.26)
# -----------------------------------------------------------------------------
st.markdown("---")
col_f1, col_f2 = st.columns([3, 1])
with col_f1:
    st.markdown("**Data Limitations:** *Estimates do not account for global asset diversification.*")
    st.caption("Sources: Forbes Real-Time Billionaires, World Bank WDI.")
with col_f2:
    st.caption(f"v2.1 | Made by Divyansh Kumar Singh | {datetime.date.today()}")
