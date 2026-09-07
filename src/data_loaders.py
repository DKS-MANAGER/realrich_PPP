"""
Dynamic Macroeconomic Data Loaders:
Fetches live PPP and sovereign exchange rate series from the World Bank Data API
with resilient local offline-first caching.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Optional, List

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(REPO_ROOT, "data", "cache")
WB_INDICATOR_PPP = "PA.NUS.PPP"  # World Bank ICP PPP conversion factor, GDP
DEFAULT_CONFIG = os.path.join(REPO_ROOT, "configs", "ppp_rates.json")

# Mapping of sovereign country names to ISO-2 codes for World Bank API
COUNTRY_ISO2_MAP = {
    "United States": "US",
    "France": "FR",
    "Spain": "ES",
    "India": "IN",
    "Mexico": "MX",
    "Germany": "DE",
    "Austria": "AT",
    "Japan": "JP",
    "Italy": "IT",
    "Canada": "CA",
    "China": "CN",
    "Hong Kong": "HK",
    "Indonesia": "ID",
    "United Kingdom": "GB",
    "Belgium": "BE",
    "Russia": "RU",
}


def fetch_world_bank_indicator(
    country_iso2: str,
    indicator: str = WB_INDICATOR_PPP,
    timeout_sec: int = 5,
) -> Optional[float]:
    """
    Fetch the most recent non-null indicator value for a country from World Bank API.
    """
    url = f"http://api.worldbank.org/v2/country/{country_iso2}/indicator/{indicator}?format=json&per_page=10"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RealRich-PPP/2.0"})
        with urllib.request.urlopen(req, timeout=timeout_sec) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if len(payload) >= 2 and isinstance(payload[1], list):
                for record in payload[1]:
                    val = record.get("value")
                    if val is not None:
                        return float(val)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception):
        return None
    return None


def get_ppp_factors_with_fallback(
    countries: Optional[List[str]] = None,
    use_live_api: bool = False,
) -> Dict[str, float]:
    """
    Retrieve sovereign PPP factors with multi-tier fallback:
    1. Live World Bank API (if use_live_api is True)
    2. Local disk cache (data/cache/worldbank_ppp_cache.json)
    3. Bundled production config (configs/ppp_rates.json)
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, "worldbank_ppp_cache.json")

    # Load baseline from configs
    baseline_factors: Dict[str, float] = {}
    if os.path.exists(DEFAULT_CONFIG):
        try:
            with open(DEFAULT_CONFIG, "r", encoding="utf-8") as f:
                baseline_factors = json.load(f).get("ppp_factors", {})
        except Exception:
            pass

    # Read from cache if present
    cached_factors: Dict[str, float] = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached_factors = json.load(f)
        except Exception:
            pass

    resolved = {**baseline_factors, **cached_factors}

    if not use_live_api:
        return resolved

    target_countries = countries or list(COUNTRY_ISO2_MAP.keys())
    updated = False

    for country in target_countries:
        iso2 = COUNTRY_ISO2_MAP.get(country)
        if not iso2:
            continue
        val = fetch_world_bank_indicator(iso2)
        if val is not None and val > 0:
            resolved[country] = round(val, 2)
            updated = True

    if updated:
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(resolved, f, indent=4)
        except Exception:
            pass

    return resolved


if __name__ == "__main__":
    factors = get_ppp_factors_with_fallback(use_live_api=False)
    print(f"[OK] Ingestion engine ready. Resolved {len(factors)} sovereign PPP factors.")
