# pip install yfinance pandas numpy neuralprophet pmdarima matplotlib

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from neuralprophet import NeuralProphet
from pmdarima import auto_arima
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def fetch_data(ticker='SI=F', period='20y'):
    """
    Fetch historical data from yfinance.
    """
    print(f"Fetching data for {ticker}...")
    data = yf.Ticker(ticker).history(period=period)
    return data

def preprocess_data(df):
    """
    Preprocess data: Calculate volatility, handle NaNs, rename columns.
    """
    print("Preprocessing data...")
    df = df.copy()
    
    # Calculate Volatility: (High-Low) rolling std (window=4, annualized)
    # Annualized factor usually sqrt(252) for daily data
    # Volatility here is defined as the standard deviation of the High-Low range
    df['Volatility'] = (df['High'] - df['Low']).rolling(window=4).std() * np.sqrt(252)
    
    # Prepare for NeuralProphet
    df = df.reset_index()
    # Ensure 'ds' is datetime and tz-naive
    df['ds'] = df['Date'].dt.tz_localize(None) 
    df['y'] = df['Close']
    
    # Select columns
    df = df[['ds', 'y', 'Volatility']]
    
    # Handle NaNs created by rolling window
    df = df.dropna()
    
    return df

def train_neural_prophet(df, forecast_days=30):
    """
    Train NeuralProphet model and forecast.
    """
    print("Training NeuralProphet model...")
    
    # Initialize model with specified hyperparameters
    m = NeuralProphet(
        growth='off',
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=True,
        n_lags=10,
        num_hidden_layers=20,
        d_hidden=36,
        learning_rate=0.003,
        n_changepoints=3,
        changepoints_range=0.95
    )
    
    # Add lagged regressor
    # Note: When n_lags > 0, NeuralProphet treats lagged regressors as autoregressive features
    m.add_lagged_regressor('Volatility')
    
    # Fit model
    metrics = m.fit(df, freq='D')
    
    # Forecast
    print(f"Forecasting {forecast_days} days ahead...")
    
    # Create future dataframe
    # n_historic_predictions=True allows us to see in-sample fit
    future = m.make_future_dataframe(df, periods=forecast_days, n_historic_predictions=True)
    forecast = m.predict(future)
    
    return m, forecast

def train_arima_alternative(df, forecast_days=30):
    """
    Train ARIMA model on log-differenced data as an alternative.
    """
    print("\nTraining ARIMA alternative...")
    
    # Log-difference transformation
    y = df['y'].values
    # Add small constant to avoid log(0) if any, though price shouldn't be 0
    y_log = np.log(y)
    
    # Differencing
    y_log_diff = np.diff(y_log)
    # Remove NaNs/Infs if any
    y_log_diff = y_log_diff[~np.isnan(y_log_diff)]
    
    # Fit auto_arima
    # Using stepwise search to speed up
    model = auto_arima(y_log_diff, seasonal=False, trace=True, 
                       error_action='ignore', suppress_warnings=True,
                       stepwise=True)
    
    print(model.summary())
    
    # Forecast
    forecast_diff = model.predict(n_periods=forecast_days)
    
    # Reconstruct predictions (inverse diff and log)
    # We need the last observed log value to reconstruct from diff
    last_log_val = y_log[-1]
    forecast_log = last_log_val + np.cumsum(forecast_diff)
    forecast_prices = np.exp(forecast_log)
    
    return forecast_prices

def evaluate_and_plot(m, forecast, df):
    """
    Evaluate metrics and plot results.
    """
    print("Evaluating and plotting...")
    
    # Plotting
    # Note: In a script, plt.show() blocks execution until window is closed.
    try:
        fig_forecast = m.plot(forecast)
        plt.title("NeuralProphet Forecast")
        plt.show()
        
        fig_components = m.plot_components(forecast)
        plt.title("Forecast Components")
        plt.show()
        
        fig_params = m.plot_parameters()
        plt.title("Model Parameters")
        plt.show()
    except Exception as e:
        print(f"Could not plot: {e}")

    # Metrics on training data (in-sample)
    # Align data: forecast contains 'yhat1' and 'ds'
    
    merged = pd.merge(df, forecast[['ds', 'yhat1']], on='ds', how='inner')
    
    # Drop NaNs (start of series might not have predictions due to lags)
    merged = merged.dropna()
    
    if not merged.empty:
        y_pred = merged['yhat1'].values
        y_true_aligned = merged['y'].values
        
        mae = mean_absolute_error(y_true_aligned, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true_aligned, y_pred))
        
        print(f"In-sample MAE: {mae:.4f}")
        print(f"In-sample RMSE: {rmse:.4f}")
    else:
        print("Not enough data for in-sample evaluation.")

def main():
    # 1. Fetch Data
    df = fetch_data()
    
    if df.empty:
        print("No data fetched. Exiting.")
        return

    # 2. Preprocess
    df_clean = preprocess_data(df)
    
    # 3. NeuralProphet
    m, forecast = train_neural_prophet(df_clean)
    
    # 4. Evaluate and Plot
    evaluate_and_plot(m, forecast, df_clean)
    
    # 5. ARIMA Alternative
    arima_preds = train_arima_alternative(df_clean)
    
    # 6. Save Results
    print("Saving results...")
    forecast.to_csv('silver_price_forecast_neuralprophet.csv', index=False)
    
    # Print last 10 forecasts
    print("\nLast 10 NeuralProphet Forecasts (Future):")
    # Filter for future dates
    last_date = df_clean['ds'].max()
    future_forecast = forecast[forecast['ds'] > last_date]
    print(future_forecast[['ds', 'yhat1']].head(10)) # First 10 of the future
    
    print("\nARIMA Forecast (Next 5 days):")
    print(arima_preds[:5])

if __name__ == "__main__":
    main()
