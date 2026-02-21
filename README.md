# Real Rich PPP — Global Wealth Analysis

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)

**Ranking the world's 50 richest people by Purchasing Power Parity (PPP)-adjusted wealth**

</div>

---

##  Key Insight

> Billionaires in emerging markets (India, China, Indonesia) appear **far wealthier** in real terms when their USD fortunes are adjusted for local purchasing power — revealing a hidden dimension of global wealth concentration invisible in nominal rankings.

---

##  What It Does

| Step | Description |
|------|-------------|
| **Data Collection** | Scrapes/loads top-50 billionaire wealth (Forbes nominal USD) |
| **PPP Adjustment** | Converts nominal USD  PPP-equivalent using World Bank IMF factors |
| **Ranking** | Re-ranks billionaires by PPP-adjusted wealth |
| **Visualisation** | Interactive charts: bubble plots, rank-shift tables, choropleth |
| **Dashboard** | Streamlit app for live exploration of all metrics |

---

##  Quick Start

```bash
git clone https://github.com/DKS-MANAGER/realrich_PPP.git
cd realrich_PPP
pip install -r wealth_dashboard/requirements.txt
```

### Run the Streamlit Dashboard
```bash
streamlit run wealth_dashboard/app.py
```

### Run the Analysis Notebook
```bash
jupyter notebook richest_listPPP.ipynb
```

---

##  Repository Structure

```
realrich_PPP/
 richest_listPPP.ipynb           Main analysis notebook
 wealth_dashboard/               Streamlit production app
    app.py
    data/
        richest_ppp.csv         Processed PPP dataset
 data_output/                    Generated reports
    top50_nominal_and_ppp.csv
    rankings_tables.md
    report.md
    TOP_MOVERS_SUMMARY.md
 charts/                         Exported visualisations
 BILLIONAIRES_PPP_ANALYSIS_README.md
 README.md
```

---

##  Sample Findings

- **Mukesh Ambani** jumps +12 ranks in PPP terms (India's low cost of living amplifies real wealth)
- **Elon Musk** drops in relative ranking when USD wealth is PPP-normalised against the US cost base
- **Chinese billionaires** show the largest positive rank shifts on average

---

##  Tech Stack

- `pandas` / `numpy` — data wrangling
- `plotly` — interactive visualisations
- `streamlit` — production dashboard
- `jupyter` — exploratory analysis

---

<div align="center">
Economics & Data Science  2025<br>
<a href="https://github.com/DKS-MANAGER">Divyansh Kumar Singh</a>
</div>
