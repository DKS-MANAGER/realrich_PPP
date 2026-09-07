"""
RealRich PPP - Streamlit Cloud Production-Grade Entrypoint.
Delegates cleanly to dashboard/app.py while ensuring path resolution,
pre-flight verification, automated ETL generation, and clean error diagnostics.
"""

from pathlib import Path
import runpy
import sys
import streamlit as st

# 1. Path Anchoring & Module Resolution
ROOT_DIR = Path(__file__).resolve().parent
for search_path in [str(ROOT_DIR), str(ROOT_DIR / "src")]:
    if search_path not in sys.path:
        sys.path.insert(0, search_path)

# 2. Pre-Flight Verification & Automated ETL
config_path = ROOT_DIR / "configs" / "ppp_rates.json"
processed_csv = ROOT_DIR / "data" / "processed" / "top50_nominal_and_ppp.csv"
raw_csv = ROOT_DIR / "data" / "raw" / "forbes_top50.csv"

# Verify configuration prerequisites
if not config_path.exists():
    st.error(
        f"🚨 **Configuration Missing:** Required PPP rates configuration file not found at "
        f"`{config_path}`. Please ensure `configs/ppp_rates.json` is present in the repository."
    )
    st.stop()

# Verify processed data artifacts; trigger automated ETL pipeline if absent
if not processed_csv.exists():
    if not raw_csv.exists():
        st.error(
            f"🚨 **Dataset Missing:** Neither processed dataset (`{processed_csv}`) "
            f"nor source ledger (`{raw_csv}`) was found in the repository."
        )
        st.stop()

    try:
        with st.spinner("Building processed wealth datasets..."):
            import src.process_data
            if hasattr(src.process_data, "main"):
                src.process_data.main()
            elif hasattr(src.process_data, "process_pipeline"):
                src.process_data.process_pipeline()
    except Exception as exc:
        st.error(f"🚨 **ETL Pipeline Error:** Failed to build processed wealth datasets:\n\n`{exc}`")
        st.stop()

# 3. Delegation to Dashboard Module
app_entrypoint = ROOT_DIR / "dashboard" / "app.py"

if not app_entrypoint.exists():
    st.error(f"🚨 **Dashboard Entrypoint Missing:** Expected dashboard file at `{app_entrypoint}`.")
    st.stop()

try:
    runpy.run_path(str(app_entrypoint), run_name="__main__")
except FileNotFoundError as fnf_err:
    st.error(
        f"🚨 **File Not Found:** A required dependency or data file could not be located during dashboard execution:\n\n"
        f"`{fnf_err}`"
    )
