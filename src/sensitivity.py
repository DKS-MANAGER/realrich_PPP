"""
Sensitivity Analysis: Impact of FX Rate Volatility on PPP Rankings.

This module quantifies how a ±X% shift in exchange rates affects:
  1. PPP-adjusted wealth values
  2. Ranking positions
  3. Uplift percentages

Useful for understanding the robustness of PPP-based conclusions.
"""

import pandas as pd
import numpy as np
from typing import Optional


def sensitivity_analysis(
    df: pd.DataFrame,
    fx_shift_pct: float = 0.10,
    country_col: str = "primary_country",
    net_worth_col: str = "net_worth_usd_billion",
    fx_col: str = "exchange_rate_local_per_USD",
    ppp_col: str = "ppp_conversion_factor",
) -> pd.DataFrame:
    """
    Compute PPP-adjusted wealth under shifted FX rates.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: country_col, net_worth_col, fx_col, ppp_col.
    fx_shift_pct : float
        Fractional shift to apply to exchange rates (e.g. 0.10 = ±10%).
    country_col, net_worth_col, fx_col, ppp_col : str
        Column name mappings.

    Returns
    -------
    pd.DataFrame
        Original DataFrame plus columns:
        - fx_shifted_up / fx_shifted_down
        - ppp_wealth_base / ppp_wealth_up / ppp_wealth_down
        - rank_base / rank_up / rank_down
        - rank_change_up / rank_change_down
    """
    result = df.copy()

    # Base calculation (Corrected formula: net_worth * (fx / ppp))
    result["ppp_wealth_base"] = (
        result[net_worth_col] * (result[fx_col] / result[ppp_col])
    )
    result["rank_base"] = (
        result["ppp_wealth_base"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    # Upward shift: FX gets higher (weaker currency, higher FX/PPP)
    result["fx_shifted_up"] = result[fx_col] * (1 + fx_shift_pct)
    result["ppp_wealth_up"] = (
        result[net_worth_col] * (result["fx_shifted_up"] / result[ppp_col])
    )
    result["rank_up"] = (
        result["ppp_wealth_up"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    result["rank_change_up"] = result["rank_base"] - result["rank_up"]

    # Downward shift: FX gets lower (stronger currency, lower FX/PPP)
    result["fx_shifted_down"] = result[fx_col] * (1 - fx_shift_pct)
    result["ppp_wealth_down"] = (
        result[net_worth_col] * (result["fx_shifted_down"] / result[ppp_col])
    )
    result["rank_down"] = (
        result["ppp_wealth_down"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    result["rank_change_down"] = result["rank_base"] - result["rank_down"]

    # Summary: how much does rank move across scenarios
    result["rank_volatility"] = result[["rank_up", "rank_down"]].max(axis=1) - \
        result[["rank_up", "rank_down"]].min(axis=1)

    return result


def summarize_sensitivity(sensitivity_df: pd.DataFrame, top_n: int = 10) -> dict:
    """
    Summarize sensitivity analysis results for reporting.
    """
    country_impact = sensitivity_df.groupby("primary_country").agg({
        "ppp_wealth_base": "mean",
        "rank_volatility": "mean"
    }).reset_index()

    wealth_range = {
        "max_wealth": float(sensitivity_df["ppp_wealth_up"].max()),
        "min_wealth": float(sensitivity_df["ppp_wealth_down"].min())
    }

    most_volatile_records = sensitivity_df.nlargest(top_n, "rank_volatility")[
        ["name", "primary_country", "rank_base", "rank_volatility"]
    ].to_dict(orient="records")

    summary = {
        "max_rank_volatility": int(sensitivity_df["rank_volatility"].max()),
        "most_volatile": most_volatile_records,
        "most_volatile_billionaires": most_volatile_records,
        "country_impact": country_impact,
        "wealth_range": wealth_range
    }
    return summary
