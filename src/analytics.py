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
    return {
        "exchange_rates": {},
        "ppp_factors": {},
        "gfcf_ppp_factors": {},
        "default_domestic_share": {}
    }


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


def compute_decomposed_ppp_wealth(
    df: pd.DataFrame,
    net_worth_col: str = "net_worth_usd",
    country_col: str = "country",
    alpha_tradability: float = 0.85,
) -> pd.DataFrame:
    """
    Compute Multi-Tier Asset-Decomposed PPP Wealth.
    
    Formula:
        Effective Multiplier:
            mu_eff = omega_dom * ((FX / P_GFCF) ** alpha) + (1 - omega_dom) * 1.0
        Where:
            omega_dom: Share of assets/revenue in domestic market (0.0 to 1.0)
            P_GFCF: World Bank Gross Fixed Capital Formation PPP conversion factor
            alpha: Tradability drag elasticity (default 0.85)
            (1 - omega_dom): Liquid / multinational portfolio valued at USD parity
            
    Returns
    -------
    pd.DataFrame
        Enriched DataFrame with decomposed PPP valuation, effective multipliers,
        decomposed uplifts, and displaced rankings.
    """
    # Start with standardized baseline
    base = compute_ppp_wealth(df, net_worth_col=net_worth_col, country_col=country_col)
    result = base.copy()
    
    rates = load_ppp_rates()
    gfcf_map = rates.get("gfcf_ppp_factors", {})
    dom_map = rates.get("default_domestic_share", {})
    
    active_country = country_col if country_col in result.columns else "country"
    
    # Map GFCF factors (falling back to standard ppp_factor if GFCF unavailable)
    if "gfcf_factor" not in result.columns:
        result["gfcf_factor"] = result[active_country].map(gfcf_map)
        result["gfcf_factor"] = result["gfcf_factor"].fillna(result["ppp_factor"]).fillna(1.0)
        
    # Map domestic revenue/asset shares (falling back to 0.65 default)
    if "domestic_share" not in result.columns:
        result["domestic_share"] = result[active_country].map(dom_map).fillna(0.65)
        
    usd_val = result["net_worth_usd"]
    fx = result["fx_rate"]
    gfcf = result["gfcf_factor"]
    omega = result["domestic_share"]
    
    # Capital goods purchasing power factor with import drag elasticity
    cap_multiplier = (fx / gfcf).clip(lower=0.01) ** alpha_tradability
    
    # Blended institutional effective multiplier
    result["decomposed_multiplier"] = (
        omega * cap_multiplier + (1.0 - omega) * 1.0
    ).round(4)
    
    result["net_worth_decomposed_ppp"] = (usd_val * result["decomposed_multiplier"]).round(2)
    
    result["decomposed_uplift_pct"] = (
        ((result["net_worth_decomposed_ppp"] - usd_val) / usd_val) * 100.0
    ).round(2)
    
    result["rank_decomposed_ppp"] = (
        result["net_worth_decomposed_ppp"].rank(ascending=False, method="min").astype(int)
    )
    result["rank_change_decomposed"] = result["rank_nominal"] - result["rank_decomposed_ppp"]
    
    return result

