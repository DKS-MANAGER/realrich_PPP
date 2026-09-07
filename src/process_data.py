"""
Data processing script: Sorts raw Forbes top 50 CSV, computes PPP metrics, 
and exports to processed and output directories.
"""

import pandas as pd
import os
import json
from analytics import compute_ppp_wealth, load_ppp_rates


def process_pipeline():
    raw_path = "data/raw/forbes_top50.csv"
    if not os.path.exists(raw_path):
        print(f"Raw file {raw_path} not found.")
        return

    df = pd.read_csv(raw_path)
    
    # 1. Sort by net_worth_usd_billion descending and reassign rank
    df = df.sort_values(by="net_worth_usd_billion", ascending=False).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)
    
    # Save sorted raw file back
    df.to_csv(raw_path, index=False)
    print(f"Sorted {raw_path} successfully.")

    # 2. Load config rates and compute PPP wealth
    rates = load_ppp_rates()
    fx_map = rates.get("exchange_rates", {})
    ppp_map = rates.get("ppp_factors", {})
    
    df["exchange_rate_local_per_USD"] = df["primary_country"].map(fx_map).fillna(1.0)
    df["ppp_conversion_factor"] = df["primary_country"].map(ppp_map).fillna(1.0)
    
    processed_df = compute_ppp_wealth(df)
    
    # Ensure processed directory exists
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data_output", exist_ok=True)
    
    processed_csv_path = "data/processed/top50_nominal_and_ppp.csv"
    output_csv_path = "data_output/top50_nominal_and_ppp.csv"
    
    processed_df.to_csv(processed_csv_path, index=False)
    processed_df.to_csv(output_csv_path, index=False)
    print(f"Generated processed datasets at {processed_csv_path} and {output_csv_path}.")


if __name__ == "__main__":
    process_pipeline()
