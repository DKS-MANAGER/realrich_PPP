# RealRich PPP — Billionaire Wealth Adjusted for Purchasing Power Parity

[![Python](https://img.shields.io/badge/Python-Jupyter-orange)](https://jupyter.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)]()
[![Status](https://img.shields.io/badge/Status-Complete-green)]()

> Analyzes the **world’s 50 richest people** by adjusting nominal USD wealth for **Purchasing Power Parity (PPP)**. Demonstrates that billionaires in emerging markets (India, China) have massively higher "real" wealth than raw USD figures suggest, while US/EU billionaires see limited PPP gains. Fully reproducible Python pipeline.

---

## Key Finding

Nominal wealth in USD systematically **underrepresents** the real purchasing power of billionaires in low-cost economies. After PPP adjustment:
- Indian/Chinese billionaires: `+40%–120%` real wealth gain vs. nominal
- US/EU billionaires: `≤5%` adjustment (USD is close to PPP baseline)

---

## Methodology

1. **Data collection**: Forbes Billionaires list (top 50) — nominal USD net worth
2. **PPP conversion**: World Bank PPP conversion factors (LCU per international $)
3. **Real wealth**: `Real Wealth ($) = Nominal Wealth (USD) × (PPP factor / USD rate)`
4. **Ranking**: Re-rank by PPP-adjusted wealth vs. nominal ranking
5. **Visualizations**: Bar charts, rank-shift plots, country-wise heatmaps

---

## Repository Structure

```
realrich_PPP/
├── data/
│   ├── forbes_top50.csv         # Scraped/curated Forbes data
│   └── worldbank_ppp_factors.csv # World Bank PPP conversion factors
├── notebooks/
│   ├── 01_data_processing.ipynb  # Clean, merge, and compute PPP wealth
│   ├── 02_analysis.ipynb         # Rank shifts, country comparisons
│   └── 03_visualizations.ipynb   # Charts, heatmaps, bar races
├── output/
│   ├── ppp_adjusted_rankings.csv
│   └── figures/                  # All generated plots
└── report/
    └── ppp_economic_report.pdf   # Comprehensive written analysis
```

---

## Usage

```bash
pip install pandas matplotlib seaborn jupyter
jupyter notebook notebooks/01_data_processing.ipynb
```

---

## Tech Stack

`Python 3` · `pandas` · `matplotlib` · `seaborn` · `Jupyter Notebook`

---

## Author

**Divyansh Kumar Singh (DKS)**  
M.Tech — IIT Kanpur  
[GitHub](https://github.com/DKS-MANAGER)
