# Silver Price Research & Forecasting System
**Project Goal**: Build a defensible, research-grade forecasting system for Silver Futures (`SI=F`) that learns from historical cycles, assesses crash risk, and produces ensemble forecasts.

## 📅 Phase 0: Problem Definition
- **Objective**: Research & Thesis (Not High-Frequency Trading)
- **Forecast Horizon**: 1-day, 7-day, and 30-day scenarios.
- **Targets**: MAPE ≤ 3%, Directional Accuracy ≥ 53%.

## 🏗️ System Architecture

### Phase 1: Data & Historical Analysis
- **Long-term**: Study of major cycles (Hunt Brothers, 2011 Peak, COVID Crash).
- **Modern Data (2004-2026)**: High-resolution daily data including:
    - Silver (`SI=F`)
    - Gold (`GC=F`)
    - Volatility (Rolling Std Dev)
    - Technicals (RSI, Moving Averages)

### Phase 2: Baseline Models
- **ARIMA**: Statistical baseline for linear trends.
- **NeuralProphet**: Modern additive model for seasonality and regime changes.

### Phase 3: Crash & Regime Analysis
- **Risk Scoring**: 0-4 scale based on RSI, Volatility, and Volume.
- **Anomaly Detection**: Z-score analysis to flag potential crashes.

### Phase 4: Hybrid Ensemble
- **Composition**:
    - 40% ARIMA
    - 40% NeuralProphet (or LSTM/GRU)
    - 20% ML Regressor (XGBoost/GradientBoosting)
- **Goal**: Combine linear, non-linear, and feature-based strengths.

### Phase 5: Walk-Forward Validation
- **Method**: Rolling window validation (e.g., Train 10y, Test 1y, Step 6m).
- **Metrics**: MAE, RMSE, MAPE, Directional Accuracy across different market regimes.

### Phase 6: Fundamental Anchor (Optional)
- **Fair Value**: Adjust forecasts based on DXY (Dollar Index) and Industrial Demand proxies.

### Phase 7: Production Pipeline
- Automated scripts for fetching data, training, and generating daily reports.
