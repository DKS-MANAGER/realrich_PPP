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

from analytics import compute_ppp_wealth
from sensitivity import sensitivity_analysis, summarize_sensitivity


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
