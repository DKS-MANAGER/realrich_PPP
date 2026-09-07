# Global Billionaire Wealth: Nominal vs PPP Dashboard

**v2.1 | Made by Divyansh Kumar Singh**

## 📊 Overview
This interactive Streamlit dashboard analyzes global billionaire wealth by adjusting for **Purchasing Power Parity (PPP)**. It provides a more realistic comparison of wealth utility across different economic environments, challenging the standard nominal USD rankings.

## 🚀 Key Features

### 1. Robust Data Processing
- **Automated Cleaning**: Handles currency conversion, column renaming, and missing value checks.
- **Smart Logic**: Calculates "PPP Uplift" (purchasing power gain) and "Rank Change" (movement in global standing).

### 2. Professional Visualizations
- **Market Overview**:
  - Compare Nominal vs. PPP wealth side-by-side.
  - Interactive "Top N" slider and sorting controls.
  - Correlation scatter plot with 1:1 diagonal reference line.
- **Analytical Deep Dive**:
  - **Uplift Bar Chart**: Identifies which billionaires gain the most from local prices.
  - **Rank Movers**: Visualizes significant jumps in global ranking after adjustment.
  - **Geographic Impact**: Split view showing Average Uplift (Bar) vs. Total Wealth Share (Donut Pie).

### 3. Data Explorer
- **Detailed Records**: Full sortable table with conditional formatting.
- **Visual Cues**: Green/Red backgrounds highlight rank improvements or drops.

## 🛠️ Installation & Usage

1. **Prerequisites**
   Ensure you have Python installed.

2. **Install Dependencies**
   ```bash
   pip install streamlit pandas plotly
   ```

3. **Run the Dashboard**
   Navigate to the project directory and run:
   ```bash
   streamlit run app.py
   ```

## 📂 Project Structure
- `app.py`: Main application logic.
- `data/richest_ppp.csv`: Source dataset.
- `assets/theme.css`: Custom dark theme and UI styling.

## 📝 Methodology
- **Nominal USD**: Wealth at standard market exchange rates (Forbes).
- **PPP Adjusted**: Wealth adjusted for local Cost of Living (World Bank WDI factors).
- **Uplift %**: Percentage increase in purchasing power derived from local cost advantages.

---
*Updated: January 2026*
