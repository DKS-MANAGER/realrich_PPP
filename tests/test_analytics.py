"""
Unit tests for PPP analytics logic.

Run with: python -m pytest tests/ -v
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from analytics import compute_ppp_wealth, compute_decomposed_ppp_wealth
from sensitivity import sensitivity_analysis, summarize_sensitivity, monte_carlo_fx_simulation
from models.clustering import segment_billionaires, segment_billionaires_gmm
from data_loaders import get_ppp_factors_with_fallback


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_df():
    """Minimal DataFrame for testing."""
    return pd.DataFrame({
        "name": ["Alice (US)", "Bob (India)", "Carol (China)"],
        "net_worth_usd_billion": [100.0, 50.0, 80.0],
        "primary_country": ["United States", "India", "China"],
        "exchange_rate_local_per_USD": [1.0, 83.42, 7.2],
        "ppp_conversion_factor": [1.0, 20.42, 3.5],
    })


# ── Analytics Tests ───────────────────────────────────────────────────────────

class TestComputePPPWealth:
    """Tests for the core PPP calculation function."""

    def test_us_unchanged(self, sample_df):
        """US billionaires should have PPP ≈ nominal (FX=1, PPP=1)."""
        result = compute_ppp_wealth(sample_df)
        us_row = result[result["primary_country"] == "United States"].iloc[0]
        assert us_row["net_worth_ppp_intl$"] == pytest.approx(100.0, abs=0.01)

    def test_india_uplift(self, sample_df):
        """India should show significant PPP uplift (FX / PPP = 83.42 / 20.42 ≈ 4.085)."""
        result = compute_ppp_wealth(sample_df)
        india_row = result[result["primary_country"] == "India"].iloc[0]
        expected_wealth = 50.0 * (83.42 / 20.42)
        assert india_row["net_worth_ppp_intl$"] == pytest.approx(expected_wealth, abs=0.01)
        assert india_row["net_worth_ppp_intl$"] > 50.0

    def test_output_columns(self, sample_df):
        """Output must contain required columns."""
        result = compute_ppp_wealth(sample_df)
        required = [
            "name", "net_worth_usd_billion", "primary_country",
            "net_worth_ppp_intl$", "pct_change_vs_nominal",
        ]
        for col in required:
            assert col in result.columns, f"Missing column: {col}"

    def test_no_nan_in_output(self, sample_df):
        """No NaN values should appear in numeric output columns."""
        result = compute_ppp_wealth(sample_df)
        numeric_cols = result.select_dtypes(include=[np.number]).columns
        assert result[numeric_cols].isna().sum().sum() == 0


# ── Sensitivity Tests ────────────────────────────────────────────────────────

class TestSensitivity:
    """Tests for the sensitivity analysis module."""

    def test_base_unchanged(self, sample_df):
        """Base PPP wealth should match direct calculation."""
        result = sensitivity_analysis(sample_df, fx_shift_pct=0.10)
        for _, row in result.iterrows():
            expected = row["net_worth_usd_billion"] * (
                row["exchange_rate_local_per_USD"] / row["ppp_conversion_factor"]
            )
            assert row["ppp_wealth_base"] == pytest.approx(expected, rel=1e-6)

    def test_fx_up_increases_wealth(self, sample_df):
        """If FX rate increases (weaker currency, higher FX/PPP), PPP wealth should increase."""
        result = sensitivity_analysis(sample_df, fx_shift_pct=0.10)
        non_us = result[result["primary_country"] != "United States"]
        assert (non_us["ppp_wealth_up"] > non_us["ppp_wealth_base"]).all()

    def test_fx_down_decreases_wealth(self, sample_df):
        """If FX rate decreases (stronger currency, lower FX/PPP), PPP wealth should decrease."""
        result = sensitivity_analysis(sample_df, fx_shift_pct=0.10)
        non_us = result[result["primary_country"] != "United States"]
        assert (non_us["ppp_wealth_down"] < non_us["ppp_wealth_base"]).all()

    def test_rank_volatility_non_negative(self, sample_df):
        """Rank volatility must be ≥ 0."""
        result = sensitivity_analysis(sample_df, fx_shift_pct=0.10)
        assert (result["rank_volatility"] >= 0).all()


class TestSummarizeSensitivity:
    """Tests for the summary function."""

    def test_returns_dict_keys(self, sample_df):
        result = sensitivity_analysis(sample_df, fx_shift_pct=0.10)
        summary = summarize_sensitivity(result)
        assert "most_volatile" in summary
        assert "country_impact" in summary
        assert "wealth_range" in summary

    def test_country_impact_is_dataframe(self, sample_df):
        result = sensitivity_analysis(sample_df, fx_shift_pct=0.10)
        summary = summarize_sensitivity(result)
        assert isinstance(summary["country_impact"], pd.DataFrame)


# ── Advanced Quantitative Upgrade Tests ───────────────────────────────────────

class TestDecomposedPPP:
    """Tests for multi-tier asset-decomposed PPP model."""

    def test_decomposed_bounds(self, sample_df):
        """Decomposed wealth should be bounded between nominal and pure consumer PPP."""
        result = compute_decomposed_ppp_wealth(sample_df)
        india_row = result[result["country"] == "India"].iloc[0]
        # In India, consumer PPP is ~204B (4.08x), nominal is 50B
        # Decomposed GFCF with domestic share should be between 50B and 204B
        assert india_row["net_worth_decomposed_ppp"] > india_row["net_worth_usd"]
        assert india_row["net_worth_decomposed_ppp"] < india_row["net_worth_ppp"]

    def test_us_anchor_decomposed(self, sample_df):
        """US decomposed PPP should remain near parity ($100B)."""
        result = compute_decomposed_ppp_wealth(sample_df)
        us_row = result[result["country"] == "United States"].iloc[0]
        assert us_row["net_worth_decomposed_ppp"] == pytest.approx(100.0, abs=0.5)

    def test_no_nan_decomposed(self, sample_df):
        result = compute_decomposed_ppp_wealth(sample_df)
        assert result["net_worth_decomposed_ppp"].isna().sum() == 0
        assert result["decomposed_multiplier"].isna().sum() == 0


class TestGMMClustering:
    """Tests for Gaussian Mixture Model archetype clustering."""

    def test_gmm_probabilities_sum_to_one(self, sample_df):
        """Posterior membership probabilities must sum to 1.0 for every individual."""
        # Create a dataframe with enough rows for 3 components
        expanded_df = pd.concat([sample_df] * 4, ignore_index=True)
        expanded_df["name"] = [f"Person_{i}" for i in range(len(expanded_df))]
        result = segment_billionaires_gmm(expanded_df, n_components=3)
        
        prob_cols = [c for c in result.columns if c.startswith("gmm_prob_c")]
        assert len(prob_cols) == 3
        row_sums = result[prob_cols].sum(axis=1)
        assert np.allclose(row_sums.to_numpy(), 1.0, atol=1e-3)

    def test_gmm_entropy_range(self, sample_df):
        """Normalized ambiguity entropy must lie in [0, 1]."""
        expanded_df = pd.concat([sample_df] * 4, ignore_index=True)
        result = segment_billionaires_gmm(expanded_df, n_components=3)
        assert (result["gmm_ambiguity"] >= 0.0).all()
        assert (result["gmm_ambiguity"] <= 1.0).all()


class TestMonteCarloSimulation:
    """Tests for stochastic Monte Carlo FX volatility simulation."""

    def test_sim_percentiles_ordered(self, sample_df):
        """5th percentile (best rank) must be <= 95th percentile (worst rank)."""
        result = monte_carlo_fx_simulation(sample_df, n_simulations=200, random_state=42)
        assert (result["sim_rank_p05"] <= result["sim_rank_p95"]).all()

    def test_var_and_cvar_positive(self, sample_df):
        """Value-at-Risk and Expected Shortfall should be non-negative and cvar >= var."""
        result = monte_carlo_fx_simulation(sample_df, n_simulations=200, random_state=42)
        assert (result["rank_var_95"] >= 0).all()
        assert (result["rank_cvar_95"] >= result["rank_var_95"] - 0.1).all()


class TestDataLoaders:
    """Tests for World Bank data loader and fallback cache."""

    def test_fallback_resolves_countries(self):
        factors = get_ppp_factors_with_fallback(use_live_api=False)
        assert isinstance(factors, dict)
        assert "India" in factors
        assert "United States" in factors
        assert factors["India"] > 0

