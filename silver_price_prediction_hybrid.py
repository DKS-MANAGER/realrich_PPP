# pip install yfinance pandas numpy matplotlib scikit-learn tensorflow

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, GRU, Conv1D, MaxPooling1D, Dropout

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

def fetch_data(ticker='SI=F', period='20y'):
    """
    Fetch historical data from yfinance.
    """
    print(f"Fetching data for {ticker}...")
    data = yf.Ticker(ticker).history(period=period)
    return data

def create_sequences(data, seq_length):
    """
    Create sequences for time series forecasting.
    X: (samples, seq_length, features)
    y: (samples, 1)
    """
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:(i + seq_length)]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

def build_hybrid_model(input_shape):
    """
    Build CNN-LSTM-GRU Hybrid Model.
    """
    model = Sequential([
        # 1. CNN Layer: Extract spatial patterns/local trends
        Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=input_shape),
        MaxPooling1D(pool_size=2),
        
        # 2. LSTM Layer: Capture long-term dependencies
        LSTM(units=64, return_sequences=True),
        Dropout(0.2),
        
        # 3. GRU Layer: Efficient sequence learning
        GRU(units=64, return_sequences=False),
        Dropout(0.2),
        
        # 4. Output Layer
        Dense(units=32, activation='relu'),
        Dense(units=1)
    ])
    
    model.compile(optimizer='adam', loss='mse')
    return model

def main():
    # 1. Fetch Data
    df = fetch_data()
    if df.empty:
        print("No data fetched.")
        return

    # Use 'Close' price
    data = df[['Close']].values
    
    # 2. Preprocess
    print("Preprocessing data...")
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    # Hyperparameters
    SEQ_LENGTH = 60  # Lookback period (e.g., past 60 days)
    FORECAST_DAYS = 30
    
    # Create sequences
    X, y = create_sequences(scaled_data, SEQ_LENGTH)
    
    # Split Train/Test (Keep last 30 days for validation/testing if we wanted, 
    # but here we train on all available to forecast future)
    # Let's split 80/20 for evaluation metrics
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Reshape for CNN/RNN: (samples, time steps, features)
    # X is already (samples, seq_length, 1)
    
    # 3. Build and Train Model
    print("Building and training Hybrid CNN-LSTM-GRU model...")
    model = build_hybrid_model((X_train.shape[1], X_train.shape[2]))
    model.summary()
    
    history = model.fit(
        X_train, y_train,
        epochs=20, # Increase for better results
        batch_size=32,
        validation_data=(X_test, y_test),
        verbose=1
    )
    
    # 4. Evaluate
    print("Evaluating model...")
    predictions = model.predict(X_test)
    predictions_inv = scaler.inverse_transform(predictions)
    y_test_inv = scaler.inverse_transform(y_test)
    
    mae = mean_absolute_error(y_test_inv, predictions_inv)
    rmse = np.sqrt(mean_squared_error(y_test_inv, predictions_inv))
    print(f"Test MAE: {mae:.4f}")
    print(f"Test RMSE: {rmse:.4f}")
    
    # Plot Training History
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.legend()
    plt.show()
    
    # Plot Test Predictions
    plt.figure(figsize=(12, 6))
    plt.plot(y_test_inv, label='Actual Price')
    plt.plot(predictions_inv, label='Predicted Price')
    plt.title('Silver Price Prediction (Test Set)')
    plt.legend()
    plt.show()
    
    # 5. Forecast Future
    print(f"Forecasting next {FORECAST_DAYS} days...")
    
    # Start with the last sequence from the full data
    last_sequence = scaled_data[-SEQ_LENGTH:]
    curr_seq = last_sequence.reshape((1, SEQ_LENGTH, 1))
    
    future_predictions = []
    
    for _ in range(FORECAST_DAYS):
        # Predict next step
        pred = model.predict(curr_seq, verbose=0)
        future_predictions.append(pred[0, 0])
        
        # Update sequence: remove first, add prediction
        # Reshape pred to (1, 1, 1) to append
        pred_reshaped = pred.reshape((1, 1, 1))
        curr_seq = np.append(curr_seq[:, 1:, :], pred_reshaped, axis=1)
        
    # Inverse transform predictions
    future_predictions = np.array(future_predictions).reshape(-1, 1)
    future_predictions_inv = scaler.inverse_transform(future_predictions)
    
    # Create dates for forecast
    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=FORECAST_DAYS, freq='B') # Business days
    
    forecast_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted_Close': future_predictions_inv.flatten()
    })
    
    print("\nFuture Forecasts:")
    print(forecast_df)
    
    # Save
    forecast_df.to_csv('silver_price_forecast_hybrid.csv', index=False)
    print("Forecast saved to 'silver_price_forecast_hybrid.csv'")
    
    # Plot Future
    plt.figure(figsize=(10, 6))
    plt.plot(df.index[-100:], df['Close'].tail(100), label='History (Last 100 days)')
    plt.plot(forecast_df['Date'], forecast_df['Predicted_Close'], label='Forecast', linestyle='--')
    plt.title(f'Silver Price Forecast (Next {FORECAST_DAYS} Days)')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
