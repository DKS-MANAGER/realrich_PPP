# Silver Price Prediction using Hybrid CNN-LSTM-GRU Model

This project implements a deep learning model to forecast Silver Futures (`SI=F`) prices. It uses a hybrid architecture combining Convolutional Neural Networks (CNN), Long Short-Term Memory (LSTM), and Gated Recurrent Units (GRU) to capture both local trends and long-term dependencies in time-series data.

## � Files
- **`silver_price_prediction_hybrid.py`**: The main Python script implementing the Hybrid CNN-LSTM-GRU model.
- **`Silver_Price_Prediction_Full_Strategy.ipynb`**: A comprehensive Jupyter Notebook implementing a 7-phase strategy including EDA, ARIMA baseline, and the Hybrid model.
- **`silver_price_forecast_hybrid.csv`**: The output file containing the 30-day price forecast.

## 📌 Overview
The goal is to predict future silver prices based on historical data fetched from Yahoo Finance. The model is trained on the past 20 years of daily closing prices and generates a forecast for the next 30 days.

## 📈 7-Phase Strategy (Notebook)
The `Silver_Price_Prediction_Full_Strategy.ipynb` notebook follows a structured progression:
1.  **Data Collection & Feature Engineering**: Download 20 years of data (SI=F), add regressors.
2.  **Exploratory Analysis & Visualization**: Stationarity testing, correlation plots.
3.  **ARIMA Baseline Model**: Quick, lightweight comparison.
4.  **Hybrid Deep Learning Model**: Primary model for accuracy (CNN-LSTM-GRU).
5.  **Walk-Forward Validation**: Test across 10+ market periods.
6.  **Risk Management & Metrics**: Sharpe ratio, directional accuracy, drawdowns.
7.  **Production Deployment**: Save models, daily forecasting pipeline.

## 🛠️ Dependencies
The project requires the following Python libraries:
- **yfinance**: For fetching historical market data.
- **pandas & numpy**: For data manipulation and numerical operations.
- **matplotlib & seaborn**: For visualization.
- **statsmodels**: For ARIMA and stationarity testing.
- **scikit-learn**: For data normalization and evaluation metrics.
- **tensorflow**: For building and training the deep learning model.

To install dependencies:
```bash
pip install yfinance pandas numpy matplotlib seaborn statsmodels scikit-learn tensorflow
```

## 🧠 How the Hybrid Model Works

### 1. Data Collection
- Fetches 20 years of historical data for Silver (`SI=F`) using `yfinance`.
- Uses the **Close** price for prediction.

### 2. Preprocessing
- **Normalization**: Scales data to the range [0, 1] using `MinMaxScaler` to improve model convergence.
- **Sequence Creation**: Creates sliding window sequences of 60 days (lookback period) to predict the next day's price.

### 3. Hybrid Model Architecture
The model combines three powerful neural network layers:
1.  **CNN (Conv1D)**: Extracts local features and short-term patterns from the time series.
2.  **LSTM (Long Short-Term Memory)**: Captures long-term dependencies and sequential patterns.
3.  **GRU (Gated Recurrent Unit)**: A more efficient variant of RNN that helps in learning temporal dependencies with fewer parameters.
4.  **Dense Layers**: Fully connected layers to map the extracted features to the final price prediction.

### 4. Training
- **Optimizer**: Adam
- **Loss Function**: Mean Squared Error (MSE)
- **Epochs**: 20
- **Batch Size**: 32

## 📊 Results & Output
- **Evaluation**: The model is evaluated on a test set (last 20% of data) using Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE).
- **Visualization**:
    - **Loss Plot**: Shows training vs. validation loss over epochs.
    - **Prediction Plot**: Compares actual vs. predicted prices for the test set.
    - **Forecast Plot**: Displays the historical price trend along with the 30-day future forecast.
- **Output File**:
    - `silver_price_forecast_hybrid.csv`: Contains the predicted prices for the next 30 business days.

## 🚀 Usage
Run the script to fetch data, train the model, and generate forecasts:
```bash
python silver_price_prediction_hybrid.py
```
The script will automatically save the forecast to a CSV file and display performance plots.
