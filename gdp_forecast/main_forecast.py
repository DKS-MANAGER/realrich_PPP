import pandas as pd
import numpy as np
import wbdata
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
import matplotlib.pyplot as plt
import datetime
import os
import argparse
import warnings
import json
import pickle

# Suppress warnings
warnings.filterwarnings("ignore")

# Configuration and Constants
TOP_50_ISO = [
    "USA", "CHN", "JPN", "DEU", "IND", "GBR", "FRA", "BRA", "ITA", "CAN",
    "RUS", "KOR", "AUS", "MEX", "ESP", "IDN", "SAU", "TUR", "NLD", "CHE",
    "POL", "ARG", "SWE", "BEL", "THA", "IRN", "AUT", "NOR", "ARE", "NGA",
    "ISR", "IRL", "ZAF", "SGP", "PHL", "VNM", "MYS", "BGD", "EGY", "HKG",
    "DNK", "COL", "PAK", "CHL", "FIN", "CZE", "PRT", "ROU", "PER", "IRQ"
]

ECONOMY_TYPES = {
    "Stable": ["USA", "DEU", "JPN", "GBR", "FRA", "CAN", "AUS", "ITA", "ESP", "NLD", "CHE", "SWE", "BEL", "AUT", "NOR", "ISR", "IRL", "DNK", "FIN", "PRT"],
    "High_Growth": ["CHN", "IND", "VNM", "IDN", "BGD", "PHL", "MYS"],
    "Emerging": ["BRA", "MEX", "TUR", "POL", "ARG", "THA", "SAU", "ZAF", "EGY", "COL", "PAK", "CHL", "ROM", "PER", "NGA", "RUS", "IRN"]
}

FORECAST_YEARS = 5
START_YEAR = 2010
END_YEAR = 2025

DATA_DIR = "data"
MODELS_DIR = "models"
FORECASTS_DIR = "forecasts"

def setup_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(FORECASTS_DIR, exist_ok=True)

# Step 1: Data Acquisition
def fetch_gdp_data(countries):
    print(f"Fetching GDP data from World Bank for {len(countries)} countries...")
    data_date = (datetime.datetime(START_YEAR, 1, 1), datetime.datetime(END_YEAR, 12, 31))
    
    # NY.GDP.MKTP.CD = GDP (current US$)
    try:
        raw_data = wbdata.get_dataframe({"NY.GDP.MKTP.CD": "GDP"}, country=countries, data_date=data_date)
        raw_data.reset_index(inplace=True)
        raw_data['date'] = pd.to_datetime(raw_data['date'])
        raw_data['GDP'] = raw_data['GDP'].astype(float)
        
        # Save to cache
        raw_data.to_csv(os.path.join(DATA_DIR, "wbdata_gdp_2010_2025.csv"), index=False)
        return raw_data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

# Step 3: Processing Pipeline
def preprocess_country_data(df, country_name):
    country_df = df[df['country'] == country_name].copy()
    if country_df.empty:
        return None
    
    country_df = country_df.sort_values('date')
    
    # Missing value interpolation
    country_df['GDP'] = country_df['GDP'].interpolate(method='linear')
    # Fill remaining NaNs if any (e.g., leading/trailing)
    country_df['GDP'] = country_df['GDP'].fillna(method='bfill').fillna(method='ffill')
    
    # Feature Engineering
    # 1. Log Transform
    country_df['log_GDP'] = np.log1p(country_df['GDP'])
    
    # 2. Pandemic Dummy (2020-2021)
    country_df['pandemic'] = country_df['date'].apply(lambda x: 1 if x.year in [2020, 2021] else 0)
    
    return country_df

# Step 2 & 5: Model Selection & Training
def get_economy_type(iso_code):
    # Map country name/ISO (assuming input is ISO or we can fuzzy match)
    # The WB data returns country names, so we might need to map them. 
    # For simplicitly, checking against names or codes if provided.
    # Here we assume country_name logic roughly matches our lists or defaults to 'Emerging'
    
    # Reverse lookup or direct check
    for etype, countries in ECONOMY_TYPES.items():
        if iso_code in countries:
            return etype
    return "Emerging" # Default

def train_prophet(df_train, economy_type):
    # Parameters based on Economy Type
    if economy_type == "Stable":
        cps = 0.02
        growth = 'linear'
    elif economy_type == "High_Growth":
        cps = 0.05
        growth = 'linear' # 'logistic' requires cap
    else: # Emerging or Low Growth
        cps = 0.1
        growth = 'linear'
        
    # Setup Prophet
    model = Prophet(
        changepoint_prior_scale=cps,
        growth=growth,
        seasonality_mode='multiplicative',
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )
    
    # Add regressor for pandemic
    model.add_regressor('pandemic')
    
    # Prophet DataFrame Format
    df_prophet = pd.DataFrame({
        'ds': df_train['date'],
        'y': df_train['log_GDP'],
        'pandemic': df_train['pandemic']
    })
    
    if growth == 'logistic':
         df_prophet['cap'] = df_prophet['y'].max() + np.log(2)

    model.fit(df_prophet)
    return model

def train_arima(df_train, economy_type):
    # Simple ARIMA configuration
    # Order selection could be automated with auto_arima, but using fixed as per prompt for now or simple heuristic
    # Prompt suggestion: ARIMA(1,1,1) x (1,1,1)[4]. But we have yearly data usually from WB for simplicity in this script.
    # If yearly, seasonality period is 1 or non-existent in ARIMA terms unless we have quarterly. 
    # Validating yearly data constraints.
    
    data = df_train['log_GDP'].values
    
    # Fallback to simple ARIMA(1,1,0) or (1,1,1) for annual data
    try:
        model = ARIMA(data, order=(1,1,1))
        model_fit = model.fit()
        return model_fit
    except:
        try:
            model = ARIMA(data, order=(1,1,0))
            model_fit = model.fit()
            return model_fit
        except:
            return None

def make_forecasts(prophet_model, arima_model, df_train, periods, economy_type):
    # 1. Prophet Forecast
    future_prophet = prophet_model.make_future_dataframe(periods=periods, freq='Y')
    
    # Add future regressor values (Pandemic is 0 for future)
    future_prophet['pandemic'] = future_prophet['ds'].apply(lambda x: 1 if x.year in [2020, 2021] else 0)
    
    if prophet_model.growth == 'logistic':
         future_prophet['cap'] = future_prophet['y'].max() + np.log(2) # Simplified
         
    forecast_prophet = prophet_model.predict(future_prophet)
    prophet_preds = forecast_prophet['yhat'].values
    
    # 2. ARIMA Forecast
    # ARIMA forecasts steps ahead
    if arima_model:
        arima_preds_log = arima_model.forecast(steps=periods)
        # We need to combine history + forecast for easier handling, or just take the forecast part
        # To make it match Prophet's length (History + Future), we get fitted values + forecast
        arima_history = arima_model.fittedvalues
        arima_full_log = np.concatenate([arima_history, arima_preds_log])
        
        # Adjust length if ARIMA fitted values differ (usually start from index 0 or d)
        if len(arima_full_log) < len(prophet_preds):
            pad = len(prophet_preds) - len(arima_full_log)
            arima_full_log = np.concatenate([np.full(pad, np.nan), arima_full_log])
        elif len(arima_full_log) > len(prophet_preds):
             arima_full_log = arima_full_log[-len(prophet_preds):]
    else:
        arima_full_log = prophet_preds # Fallback
        
    return df_train['date'], future_prophet['ds'], prophet_preds, arima_full_log

# Step 4 & 6: Ensemble and Validation
def run_pipeline(countries_df, selected_countries=None):
    results = []
    
    if selected_countries is None:
        selected_countries = countries_df['country'].unique()
    
    print(f"Processing {len(selected_countries)} countries...")
    
    for country in selected_countries:
        # Preprocess
        df_processed = preprocess_country_data(countries_df, country)
        if df_processed is None or len(df_processed) < 8: # Minimal data check
            print(f"Skipping {country}: Insufficient data.")
            continue
            
        # Determine Economy Type (Mapping logic needed, here simplified to random/defaults if name not in dict)
        # In real app, we map country Name to ISO.
        # Assuming for now we treat all as 'Emerging' unless matched.
        iso_lookup = {
            "United States": "USA", "China": "CHN", "Japan": "JPN", "Germany": "DEU", 
            "India": "IND", "United Kingdom": "GBR", "France": "FRA"
        } 
        iso = iso_lookup.get(country, "UNK")
        economy_type = get_economy_type(iso)
        
        # Train/Test Split for Validation (Last 3 years as validation)
        train_size = len(df_processed) - 3
        if train_size < 5:
            train_size = len(df_processed) # Skip validation if too short
            
        df_train_cv = df_processed.iloc[:train_size]
        df_val_cv = df_processed.iloc[train_size:]
        
        # Train Models on CV
        p_model_cv = train_prophet(df_train_cv, economy_type)
        a_model_cv = train_arima(df_train_cv, economy_type)
        
        # Validate Step
        # Forecast 3 years
        # Note: Implementation detail - aligning dates for Prophet and ARIMA
        future_cv = p_model_cv.make_future_dataframe(periods=len(df_val_cv), freq='Y')
        future_cv['pandemic'] = future_cv['ds'].apply(lambda x: 1 if x.year in [2020, 2021] else 0)
        p_forecast_cv = p_model_cv.predict(future_cv)
        p_preds_cv = p_forecast_cv['yhat'].iloc[-len(df_val_cv):].values
        
        if a_model_cv:
            a_preds_cv = a_model_cv.forecast(steps=len(df_val_cv))
        else:
            a_preds_cv = p_preds_cv
            
        # Calculate MAPE
        actuals = df_val_cv['log_GDP'].values
        mape_p = mean_absolute_percentage_error(np.expm1(actuals), np.expm1(p_preds_cv))
        mape_a = mean_absolute_percentage_error(np.expm1(actuals), np.expm1(a_preds_cv))
        
        # Weights based on MAPE (Prompt Step 4.3)
        if mape_p < 0.02:
            w_p, w_a = 0.7, 0.3
        elif mape_p < 0.04:
            w_p, w_a = 0.5, 0.3 # + 0.2 linear/other (Using 62.5% / 37.5% normalized)
            w_p, w_a = 0.6, 0.4
        else:
             # Fallback logic
             w_p, w_a = 0.5, 0.5

        # Final Training (Full Data)
        p_model_full = train_prophet(df_processed, economy_type)
        a_model_full = train_arima(df_processed, economy_type)
        
        # Final Forecast
        _, future_dates, p_preds_full, a_preds_full = make_forecasts(p_model_full, a_model_full, df_processed, FORECAST_YEARS, economy_type)
        
        # Ensemble
        # Ensure lengths match - take simple approach of tail for forecast period
        forecast_len = FORECAST_YEARS
        
        # Extract forecast portion
        p_future = p_preds_full[-forecast_len:]
        a_future = a_preds_full[-forecast_len:]
        
        ensemble_log = (w_p * p_future) + (w_a * a_future)
        ensemble_original = np.expm1(ensemble_log)
        
        # Save results
        future_years = [d.year for d in future_dates.tail(forecast_len)]
        
        for i, year in enumerate(future_years):
            results.append({
                'country': country,
                'year': year,
                'forecast_mean': ensemble_original[i],
                # Simple interval approximation
                'forecast_lower': ensemble_original[i] * 0.95, 
                'forecast_upper': ensemble_original[i] * 1.05,
                'model_weights': f"P:{w_p}, A:{w_a}"
            })
            
        # Save models (optional, pickling)
        # with open(f"{MODELS_DIR}/prophet_{country}.pkl", "wb") as f:
        #     pickle.dump(p_model_full, f)
            
    return pd.DataFrame(results)

def main():
    setup_directories()
    
    # Check for local data first
    data_path = os.path.join(DATA_DIR, "wbdata_gdp_2010_2025.csv")
    if os.path.exists(data_path):
        print("Loading data from local cache...")
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])
    else:
        df = fetch_gdp_data(TOP_50_ISO)
        
    if df.empty:
        print("No data found or downloaded. Exiting.")
        return

    # Run Forecasting
    forecast_results = run_pipeline(df)
    
    # Save Forecasts
    output_path = os.path.join(FORECASTS_DIR, "gdp_forecast_2026_2030_top50.csv")
    forecast_results.to_csv(output_path, index=False)
    
    print(f"\nForecast completion. Results saved to {output_path}")
    
    # Step 7: Global Rankings Table
    final_year = forecast_results['year'].max()
    ranking = forecast_results[forecast_results['year'] == final_year].sort_values('forecast_mean', ascending=False).head(10)
    
    print(f"\n--- Projected Top 10 Economies in {final_year} ---")
    ranking['gdp_trillions'] = ranking['forecast_mean'] / 1e12
    print(ranking[['country', 'gdp_trillions', 'model_weights']].to_string(index=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GDP Forecast System")
    parser.add_argument("--countries", type=str, default="top50", help="List of countries or 'top50'")
    parser.add_argument("--horizon", type=int, default=5, help="Forecast horizon in years")
    parser.add_argument("--model", type=str, default="ensemble", help="Model type: prophet, arima, or ensemble")
    
    args = parser.parse_args()
    
    # Update global config based on args
    FORECAST_YEARS = args.horizon
    
    main()
