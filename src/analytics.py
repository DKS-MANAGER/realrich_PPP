"""
Analytics module for Purchasing Power Parity (PPP) Billionaire Wealth Analysis.
Provides functions for computing PPP-adjusted wealth, rankings, and uplifts.
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Optional


def load_ppp_rates(config_path: Optional[str] = None) -> dict:
    """Load exchange rates and PPP factors from config file."""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "ppp_rates.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"exchange_rates": {}, "ppp_factors": {}}


def compute_ppp_wealth(
    df: pd.DataFrame,
    net_worth_col: str = "net_worth_usd_billion",
    country_col: str = "primary_country",
    fx_col: str = "exchange_rate_local_per_USD",
    ppp_col: str = "ppp_conversion_factor",
) -> pd.DataFrame:
    """
    Compute PPP-adjusted net worth and rankings for billionaires.
    
    Formula: net_worth_ppp_intl$ = net_worth_usd * (fx / ppp)
    """
    result = df.copy()
    
    # Ensure columns exist or map from config if available
    rates = load_ppp_rates()
    fx_map = rates.get("exchange_rates", {})
    ppp_map = rates.get("ppp_factors", {})
    
    if fx_col not in result.columns and country_col in result.columns:
        result[fx_col] = result[country_col].map(fx_map).fillna(1.0)
    if ppp_col not in result.columns and country_col in result.columns:
        result[ppp_col] = result[country_col].map(ppp_map).fillna(1.0)
        
    # Correct PPP wealth calculation
    result["net_worth_ppp_intl$"] = result[net_worth_col] * (result[fx_col] / result[ppp_col])
    
    # Uplift percentage (both naming conventions supported)
    pct_change = (
        (result["net_worth_ppp_intl$"] - result[net_worth_col]) / result[net_worth_col]
    ) * 100.0
    result["ppp_uplift_pct"] = pct_change
    result["pct_change_vs_nominal"] = pct_change
    
    # Nominal rank (if not present)
    if "rank" not in result.columns:
        result["rank"] = result[net_worth_col].rank(ascending=False, method="min").astype(int)
        
    # PPP rank
    result["ppp_rank"] = (
        result["net_worth_ppp_intl$"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    
    # Rank change (positive means rank improved / numerical position decreased)
    result["rank_change"] = result["rank"] - result["ppp_rank"]
    
    return result
