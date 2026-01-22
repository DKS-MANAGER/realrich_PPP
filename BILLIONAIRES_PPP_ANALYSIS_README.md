# World's Richest People: PPP-Adjusted Wealth Analysis
**Analysis Date:** January 22, 2026  
**Status:** ✓ Complete - All deliverables generated

---

## 📋 Executive Summary

This comprehensive analysis examines the wealth of the world's 50 richest individuals through the lens of **Purchasing Power Parity (PPP)**. By adjusting for differences in the "Cost of Living" across 12 different nations (including India, China, USA, France, and Indonesia), we reveal the *real* domestic purchasing power of these billionaires.

### Key Findings
*   **Total Nominal Wealth:** ~$4.5 Trillion USD
*   **Total PPP-Adjusted Wealth:** ~$5.8 Trillion Int$
*   **Biggest Relative Winner:** **Mukesh Ambani (India)** (+308.5% increase)
*   **Most Impacted Region:** Emerging Markets (India, Indonesia, Russia, China) show massive purchasing power premiums (2x - 4x).
*   **Least Impacted:** US and Eurozone billionaires (Exchange rates closely match PPP).

---

## 📦 Deliverables Produced

The analytical pipeline (`richest_listPPP.ipynb`) automatically improved and generated the following assets:

### 1. Data Tables
📁 **Location:** `data_output/`

| File | Format | Description |
|------|--------|-------------|
| `top50_nominal_and_ppp.csv` | CSV | **Master Dataset** containing all 50 individuals, exchange rates, PPP factors, and calculated metrics. |
| `rankings_tables.md` | Markdown | Formatted tables displaying the rankings before and after PPP adjustment. |
| `report.md` | Markdown | A detailed 1,200-word report covering methodology, sensitivity analysis, and economic interpretation. |

### 2. Visualizations
📁 **Location:** `charts/`

| Chart | Purpose |
|-------|---------|
| `top20_nominal_vs_ppp.png` | **Comparative Bar Chart**: Visualizes the dramatic jump for non-US billionaires. |
| `scatter_nominal_vs_ppp.png` | **Scatter Analysis**: Shows the deviation from the "Equal Value" line (Nominal = PPP). |
| `top_movers_ppp.png` | **Impact Analysis**: Highlights the Top 10 Gainers vs. the Least Impacted (Stable) individuals. |
| `avg_ppp_gain_by_country.png`| **Country Index**: Average purchasing power multiplier by nation. |
| `wealth_distribution_donut.png`| **Geographic Split**: Share of total PPP wealth by country. |

### 3. Source Code
📄 **Main Notebook:** `richest_listPPP.ipynb`

An interactive, reproducible Jupyter Notebook that:
1.  **Ingests** raw net worth and economic data.
2.  **Calculates** local currency and PPP-adjusted values (Int$).
3.  **Visualizes** key insights using Matplotlib/Seaborn.
4.  **Exports** professional-grade reports and datasets.

---

## 🔍 Methodology Snapshot

The analysis uses the standard PPP conversion formula:

$$ \text{PPP Wealth} = \frac{\text{Nominal USD} \times \text{Exchange Rate (LCU/\$)}}{\text{PPP Conversion Factor (LCU/Int\$)}} $$

**Interpretation:**
*   If `Exchange Rate > PPP Factor`: The local currency is undervalued; **Wealth Increases**.
*   If `Exchange Rate ≈ PPP Factor`: The local currency is at parity; **Wealth is Stable**.

**Data Sources:**
*   **Wealth:** Forbes Real-Time Billionaires (Top 50 Snapshot)
*   **PPP Factors:** World Bank WDI (2025 Estimates)
*   **Exchange Rates:** Market rates as of Jan 2026

---

## 📈 Guide to Results

### Who Gains the Most?
Billionaires in **India**, **Indonesia**, and **Russia** see their wealth multiply by **3x to 4x** in domestic terms.
*   *Example:* **Mukesh Ambani** (India) jumps from ~$110B (Nominal) to over ~$440B (PPP), reflecting the low cost of labor and services in India.

### Who Stays the Same?
Billionaires in the **United States** (e.g., Elon Musk, Jeff Bezos) stay at **0.0% change**.
*   *Reason:* The US Dollar is the baseline currency. Purchasing power in the US is the standard against which others are measured.

---

## 🔄 How to Reproduce

1.  Open `richest_listPPP.ipynb` in VS Code.
2.  Ensure you have the required libraries: `pandas`, `matplotlib`, `seaborn`.
3.  Run the **"Run All"** command to execute the pipeline.
4.  Check the `data_output/` folder for fresh files.

---

**Project maintained by:** VS Code Copilot Agent
**Last Updated:** Jan 22, 2026
