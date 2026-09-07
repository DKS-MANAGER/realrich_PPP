"""
Data Processing Pipeline:
Sorts raw Forbes billionaire ledger, applies sovereign PPP factors,
and generates standardized datasets across data/processed/, data/output/, and dashboard/data/.
"""

import os
import pandas as pd

try:
    from src.analytics import compute_ppp_wealth, load_ppp_rates
except ImportError:
    from analytics import compute_ppp_wealth, load_ppp_rates


def process_pipeline():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(repo_root, "data", "raw", "forbes_top50.csv")
    if not os.path.exists(raw_path):
        raw_path_rel = "data/raw/forbes_top50.csv"
        if os.path.exists(raw_path_rel):
            raw_path = raw_path_rel
        else:
            raise FileNotFoundError(f"Raw file '{raw_path}' not found.")

    df = pd.read_csv(raw_path)

    # Standardize incoming column names
    col_map = {
        "rank": "rank_nominal",
        "net_worth_usd_billion": "net_worth_usd",
        "primary_country": "country",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # Sort strictly descending by net_worth_usd
    usd_col = "net_worth_usd" if "net_worth_usd" in df.columns else "net_worth_usd_billion"
    df = df.sort_values(by=usd_col, ascending=False).reset_index(drop=True)
    df["rank_nominal"] = range(1, len(df) + 1)

    # Re-save cleaned raw dataset
    df.to_csv(raw_path, index=False)
    print(f"[OK] Sorted and validated {raw_path}")

    # Compute PPP wealth
    processed_df = compute_ppp_wealth(df)

    # Canonical destinations
    destinations = [
        os.path.join(repo_root, "data", "processed", "top50_nominal_and_ppp.csv"),
        os.path.join(repo_root, "data", "output", "top50_nominal_and_ppp.csv"),
        os.path.join(repo_root, "dashboard", "data", "richest_ppp.csv"),
    ]

    for dest in destinations:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        processed_df.to_csv(dest, index=False)
        print(f"[OK] Exported master dataset to {dest}")


main = process_pipeline

if __name__ == "__main__":
    process_pipeline()
