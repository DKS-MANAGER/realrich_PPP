# World's Richest People: PPP-Adjusted Wealth Analysis
**Analysis Date:** January 22, 2026
**Status:** ✓ Complete - All deliverables generated

---

## 📋 Executive Summary

This comprehensive analysis examines the wealth of the world's top billionaires through the lens of **Purchasing Power Parity (PPP)**. By adjusting for differences in the "Cost of Living" across nations (including India, China, USA, France, and Indonesia), we reveal the *real* domestic purchasing power of these billionaires.

### Key Findings
*   **Total Nominal Wealth:** ~$4.5 Trillion USD
*   **Total PPP-Adjusted Wealth:** ~$5.8 Trillion Int$
*   **Biggest Relative Winner:** **Mukesh Ambani (India)**
*   **Most Impacted Region:** Emerging Markets (India, Indonesia, Russia, China) show massive purchasing power premiums (2x - 4x).
*   **Least Impacted:** US and Eurozone billionaires (Exchange rates closely match PPP).

---

## 📦 Deliverables Produced

The analytical pipeline (`src/process_data.py` and `richest_listPPP.ipynb`) automatically generated the following assets:

### 1. Data Tables
📁 **Location:** `data_output/` and `data/processed/`

| File | Format | Description |
|------|--------|-------------|
| `top50_nominal_and_ppp.csv` | CSV | **Master Dataset** containing all 50 individuals, exchange rates, PPP factors, and calculated metrics. |
| `rankings_tables.md` | Markdown | Formatted tables displaying the rankings before and after PPP adjustment. |
| `report.md` | Markdown | A detailed report covering methodology, sensitivity analysis, and economic interpretation. |

### 2. Visualizations
📁 **Location:** `charts/`

| Chart | Purpose |
|-------|---------|
| `top20_nominal_vs_ppp.png` | **Comparative Bar Chart**: Visualizes the dramatic jump for non-US billionaires. |
| `scatter_nominal_vs_ppp.png` | **Scatter Plot**: Highlights outliers and non-linearities. |
| `avg_ppp_gain_by_country.png` | **Country-Level Aggregation**: Shows average uplift percentage by nation. |
| `top_movers_ppp.png` | **Rank Volatility**: Who gains the most positions when switching to PPP? |
| `wealth_distribution_donut.png` | **Global Wealth Share**: Nominal vs. PPP share distribution. |

---

## 🔬 Technical Modules & Architecture

- **`src/analytics.py`**: Core PPP calculations, ranking adjustments, and metric computations.
- **`src/sensitivity.py`**: FX rate volatility sensitivity analysis (±X% shocks).
- **`src/process_data.py`**: Robust data pipeline sorting raw data and generating processed outputs.
- **`src/models/clustering.py`**: Machine Learning K-Means clustering for UHNWI wealth archetype segmentation.
- **`wealth_dashboard/app.py`**: Interactive Streamlit dashboard for exploring metrics, charts, and what-if scenarios.
- **`tests/test_analytics.py`**: Comprehensive pytest test suite.

---

## 🚀 Running the Project

1. **Run Tests:**
   ```bash
   python -m pytest tests/ -v
   ```
2. **Process Data:**
   ```bash
   python src/process_data.py
   ```
3. **Launch Streamlit Dashboard:**
   ```bash
   streamlit run wealth_dashboard/app.py
   ```
