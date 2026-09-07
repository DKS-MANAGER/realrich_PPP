"""
Core Analytics Engine: Computes real domestic purchasing power parity (PPP) metrics.
Provides standardized variables and backward-compatible aliases.
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Optional


def load_ppp_rates(config_path: Optional[str] = None) -> dict:
    """Load sovereign exchange rates and PPP conversion factors from config."""
    if config_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(base_dir, "..", "configs", "ppp_rates.json"),
            "configs/ppp_rates.json",
        ]
        for c in candidates:
            if os.path.exists(c):
                config_path = c
                break

    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"exchange_rates": {}, "ppp_factors": {}}


def compute_ppp_wealth(
    df: pd.DataFrame,
    net_worth_col: str = "net_worth_usd",
    country_col: str = "country",
    fx_col: str = "fx_rate",
    ppp_col: str = "ppp_factor",
) -> pd.DataFrame:
    """
    Compute PPP-adjusted net worth and rankings for billionaires.
    
    Formula:
        net_worth_ppp = net_worth_usd * (fx_rate / ppp_factor)
        ppp_uplift_pct = ((net_worth_ppp - net_worth_usd) / net_worth_usd) * 100
        rank_change = rank_nominal - rank_ppp
    """
    result = df.copy()

    # Column name normalization mappings
    aliases = {
        "net_worth_usd_billion": "net_worth_usd",
        "net_worth_USD": "net_worth_usd",
        "primary_country": "country",
        "exchange_rate_local_per_USD": "fx_rate",
        "PPP_conversion_factor": "ppp_factor",
        "rank": "rank_nominal",
    }
    for old_col, new_col in aliases.items():
        if old_col in result.columns and new_col not in result.columns:
            result[new_col] = result[old_col]

    # Handle input parameters if old names passed explicitly
    if net_worth_col in result.columns:
        active_usd = net_worth_col
    elif "net_worth_usd" in result.columns:
        active_usd = "net_worth_usd"
    elif "net_worth_usd_billion" in result.columns:
        active_usd = "net_worth_usd_billion"
    else:
        raise KeyError("Could not find net worth USD column.")

    active_country = country_col if country_col in result.columns else "country"
    if active_country not in result.columns and "primary_country" in result.columns:
        active_country = "primary_country"

    # Map rates from config if missing
    rates = load_ppp_rates()
    fx_map = rates.get("exchange_rates", {})
    ppp_map = rates.get("ppp_factors", {})

    active_fx = fx_col if fx_col in result.columns else "fx_rate"
    if active_fx not in result.columns:
        result["fx_rate"] = result[active_country].map(fx_map).fillna(1.0)
        active_fx = "fx_rate"

    active_ppp = ppp_col if ppp_col in result.columns else "ppp_factor"
    if active_ppp not in result.columns:
        result["ppp_factor"] = result[active_country].map(ppp_map).fillna(1.0)
        active_ppp = "ppp_factor"

    # Enforce strict sort on nominal wealth
    result = result.sort_values(by=active_usd, ascending=False).reset_index(drop=True)
    result["rank_nominal"] = range(1, len(result) + 1)

    # Core Econometric Calculations
    result["ppp_multiplier"] = (result[active_fx] / result[active_ppp]).round(4)
    result["net_worth_ppp"] = (result[active_usd] * result["ppp_multiplier"]).round(2)
    
    # Uplift %
    result["ppp_uplift_pct"] = (
        ((result["net_worth_ppp"] - result[active_usd]) / result[active_usd]) * 100.0
    ).round(2)

    # PPP Rank & Position Changes
    result["rank_ppp"] = (
        result["net_worth_ppp"].rank(ascending=False, method="min").astype(int)
    )
    result["rank_change"] = result["rank_nominal"] - result["rank_ppp"]

    # Backward-compatible column aliases for existing notebooks and tests
    result["net_worth_usd_billion"] = result[active_usd]
    result["net_worth_ppp_intl$"] = result["net_worth_ppp"]
    result["net_worth_PPP_intl$"] = result["net_worth_ppp"]
    result["pct_change_vs_nominal"] = result["ppp_uplift_pct"]
    result["percent_difference_vs_nominal_USD"] = result["ppp_uplift_pct"]
    result["primary_country"] = result[active_country]
    result["exchange_rate_local_per_USD"] = result[active_fx]
    result["ppp_conversion_factor"] = result[active_ppp]
    result["rank"] = result["rank_nominal"]

    return result
