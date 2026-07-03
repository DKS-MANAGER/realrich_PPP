# realrich_PPP

Analyzes the world's 50 richest people by adjusting nominal USD wealth for Purchasing Power Parity (PPP). Shows massive "real" wealth gains for billionaires in emerging markets (India, China) vs. the US/EU.

## Methodology
- Fetch Forbes/Bloomberg billionaire wealth data
- Apply IMF PPP conversion factors by country
- Compute PPP-adjusted real wealth rankings
- Visualize shifts between nominal vs. real rankings

## Stack
- **Language**: Python (Jupyter Notebook)
- **Libraries**: pandas, matplotlib, seaborn, numpy
- **Output**: CSVs + visualizations + economic report

## Quick Start
```bash
pip install pandas matplotlib seaborn
jupyter notebook realrich_PPP.ipynb
```

## Key Finding
Billionaires in high-PPP countries (India, China) have significantly higher real purchasing power than nominal USD figures suggest.

## Status
Complete — reproducible pipeline with full report generated.
