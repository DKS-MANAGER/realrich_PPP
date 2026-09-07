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


def monte_carlo_fx_simulation(
    df: pd.DataFrame,
    n_simulations: int = 1000,
    volatility_std: float = 0.12,
    correlation: float = 0.35,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Multivariate Monte Carlo simulation of sovereign FX shocks and rank vulnerability.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with billionaire metrics.
    n_simulations : int
        Number of stochastic simulation paths (default: 1000).
    volatility_std : float
        Annualized/horizon FX volatility standard deviation (default: 0.12 = 12%).
    correlation : float
        Cross-currency correlation to the global dollar cycle (default: 0.35).
    random_state : int
        Random seed for reproducibility.
        
    Returns
    -------
    pd.DataFrame
        Enriched DataFrame with empirical simulated rank percentiles, VaR(95%),
        and Expected Shortfall (CVaR).
    """
    rng = np.random.default_rng(random_state)
    result = df.copy()

    usd_col = "net_worth_usd" if "net_worth_usd" in result.columns else "net_worth_usd_billion"
    country_col = "country" if "country" in result.columns else "primary_country"
    fx_col = "fx_rate" if "fx_rate" in result.columns else "exchange_rate_local_per_USD"
    ppp_col = "ppp_factor" if "ppp_factor" in result.columns else "PPP_conversion_factor"
    if ppp_col not in result.columns and "ppp_conversion_factor" in result.columns:
        ppp_col = "ppp_conversion_factor"

    countries = result[country_col].unique().tolist()
    n_c = len(countries)

    # Correlated equity/FX shock covariance matrix: Sigma = sigma^2 * [rho + (1-rho)*I]
    cov = np.full((n_c, n_c), correlation * (volatility_std ** 2))
    np.fill_diagonal(cov, volatility_std ** 2)

    # Cholesky decomposition for correlated normal variates
    L = np.linalg.cholesky(cov)
    uncorrelated = rng.standard_normal(size=(n_c, n_simulations))
    correlated = L @ uncorrelated  # Shape: (n_c, n_simulations)

    # Map country to index
    c_idx_map = {c: idx for idx, c in enumerate(countries)}

    # Base PPP wealth and nominal rank
    base_ppp = result[usd_col] * (result[fx_col] / result[ppp_col])
    base_rank = base_ppp.rank(ascending=False, method="min").astype(int)
    result["base_ppp_wealth"] = base_ppp.round(2)
    result["base_ppp_rank"] = base_rank

    n_entities = len(result)
    sim_ranks = np.zeros((n_entities, n_simulations), dtype=int)

    # Pre-extract vector values
    w_usd = result[usd_col].to_numpy()
    fx_base = result[fx_col].to_numpy()
    ppp_fac = result[ppp_col].to_numpy()
    c_indices = np.array([c_idx_map[c] for c in result[country_col]])
    is_us = np.array([c == "United States" for c in result[country_col]])

    for s in range(n_simulations):
        # Geometric brownian drift-adjusted shock: S = exp(Z - 0.5 * sigma^2)
        shocks = np.exp(correlated[:, s] - 0.5 * (volatility_std ** 2))
        entity_shocks = shocks[c_indices]
        entity_shocks[is_us] = 1.0  # US dollar is baseline anchor

        sim_fx = fx_base * entity_shocks
        sim_ppp_w = w_usd * (sim_fx / ppp_fac)

        # Rank descending (highest wealth = rank 1)
        sim_ranks[:, s] = pd.Series(sim_ppp_w).rank(ascending=False, method="min").to_numpy()

    # Aggregate stochastic statistics
    result["sim_rank_mean"] = sim_ranks.mean(axis=1).round(1)
    result["sim_rank_median"] = np.median(sim_ranks, axis=1).astype(int)
    result["sim_rank_p05"] = np.percentile(sim_ranks, 5, axis=1).astype(int)   # Best-case rank
    result["sim_rank_p95"] = np.percentile(sim_ranks, 95, axis=1).astype(int)  # Worst-case rank
    result["sim_rank_std"] = sim_ranks.std(axis=1).round(2)

    # Value-at-Risk (95% worst rank drop)
    rank_drops = sim_ranks - base_rank.to_numpy()[:, None]
    result["rank_var_95"] = np.maximum(0, np.percentile(rank_drops, 95, axis=1)).astype(int)

    # Expected Shortfall (CVaR 95%): average rank degradation in top 5% worst scenarios
    cvar_list = []
    for i in range(n_entities):
        drops = rank_drops[i, :]
        p95 = np.percentile(drops, 95)
        tail = drops[drops >= p95]
        cvar_list.append(round(float(tail.mean()), 1) if len(tail) > 0 else float(p95))
    result["rank_cvar_95"] = cvar_list

    return result

