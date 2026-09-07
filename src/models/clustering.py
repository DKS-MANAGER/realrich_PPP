"""
UHNWI Wealth Archetype Segmentation Model using K-Means Clustering.
Segments billionaires based on nominal wealth, PPP-adjusted wealth, and PPP uplift.
"""

import os
from typing import Optional, List
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

try:
    from src.analytics import compute_ppp_wealth
except ImportError:
    from analytics import compute_ppp_wealth


def segment_billionaires(
    df: pd.DataFrame,
    n_clusters: int = 3,
    features: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Apply K-Means clustering to segment billionaires into wealth archetypes.
    """
    result = df.copy()

    # If PPP metrics are not yet computed, compute them automatically
    if "net_worth_ppp" not in result.columns and "net_worth_PPP_intl$" not in result.columns:
        result = compute_ppp_wealth(result)

    usd_col = "net_worth_usd" if "net_worth_usd" in result.columns else "net_worth_usd_billion"
    ppp_col = "net_worth_ppp" if "net_worth_ppp" in result.columns else "net_worth_PPP_intl$"
    uplift_col = "ppp_uplift_pct" if "ppp_uplift_pct" in result.columns else "pct_change_vs_nominal"

    if features is None:
        features = [usd_col, ppp_col, uplift_col]

    # Ensure all requested features exist
    for f in features:
        if f not in result.columns:
            raise ValueError(f"Feature '{f}' not found in DataFrame.")

    X = result[features].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    result["archetype_cluster"] = clusters

    # Map clusters to descriptive labels based on mean nominal net worth
    cluster_means = result.groupby("archetype_cluster")[usd_col].mean().sort_values()
    sorted_cluster_ids = cluster_means.index.tolist()

    label_mapping = {}
    if n_clusters == 3:
        label_mapping[sorted_cluster_ids[0]] = "Emerging PPP Beneficiaries"
        label_mapping[sorted_cluster_ids[1]] = "Established Global Elite"
        label_mapping[sorted_cluster_ids[2]] = "Ultra-High Net Worth Titans"
    else:
        for idx, cid in enumerate(sorted_cluster_ids):
            label_mapping[cid] = f"Archetype Group {idx + 1}"

    result["archetype_label"] = result["archetype_cluster"].map(label_mapping)

    return result


def segment_billionaires_gmm(
    df: pd.DataFrame,
    n_components: int = 3,
    features: Optional[List[str]] = None,
    covariance_type: str = "full",
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Apply Gaussian Mixture Model (GMM) clustering with soft posterior probabilities.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing billionaire metrics.
    n_components : int
        Number of mixture components (default: 3).
    features : list of str, optional
        Features to use for clustering.
    covariance_type : str
        Type of covariance parameters ('full', 'tied', 'diag', 'spherical').
    random_state : int
        Random seed for reproducibility.
        
    Returns
    -------
    pd.DataFrame
        Original DataFrame with 'gmm_cluster', 'gmm_label', posterior probability columns,
        max confidence, and assignment entropy.
    """
    result = df.copy()

    # If PPP metrics are not yet computed, compute them automatically
    if "net_worth_ppp" not in result.columns and "net_worth_PPP_intl$" not in result.columns:
        result = compute_ppp_wealth(result)

    usd_col = "net_worth_usd" if "net_worth_usd" in result.columns else "net_worth_usd_billion"
    ppp_col = "net_worth_ppp" if "net_worth_ppp" in result.columns else "net_worth_PPP_intl$"
    uplift_col = "ppp_uplift_pct" if "ppp_uplift_pct" in result.columns else "pct_change_vs_nominal"

    if features is None:
        features = [usd_col, ppp_col, uplift_col]

    for f in features:
        if f not in result.columns:
            raise ValueError(f"Feature '{f}' not found in DataFrame.")

    X = result[features].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    gmm = GaussianMixture(
        n_components=n_components,
        covariance_type=covariance_type,
        random_state=random_state,
        n_init=5
    )
    gmm.fit(X_scaled)
    clusters = gmm.predict(X_scaled)
    probs = gmm.predict_proba(X_scaled)

    result["gmm_cluster"] = clusters

    # Assign posterior probability columns
    for i in range(n_components):
        result[f"gmm_prob_c{i}"] = probs[:, i].round(4)

    result["gmm_max_prob"] = probs.max(axis=1).round(4)
    # Normalized Shannon entropy across clusters (0 = completely confident, 1 = maximum ambiguity)
    entropy = -np.sum(probs * np.log(probs + 1e-12), axis=1) / np.log(n_components)
    result["gmm_ambiguity"] = entropy.round(4)

    # Order components by mean nominal net worth for interpretable labels
    comp_means = result.groupby("gmm_cluster")[usd_col].mean().sort_values()
    sorted_ids = comp_means.index.tolist()

    label_map = {}
    if n_components == 3:
        label_map[sorted_ids[0]] = "Emerging PPP Beneficiaries"
        label_map[sorted_ids[1]] = "Established Global Elite"
        label_map[sorted_ids[2]] = "Ultra-High Net Worth Titans"
    else:
        for idx, cid in enumerate(sorted_ids):
            label_map[cid] = f"GMM Archetype {idx + 1}"

    result["gmm_label"] = result["gmm_cluster"].map(label_map)
    result.attrs["gmm_bic"] = round(float(gmm.bic(X_scaled)), 2)
    result.attrs["gmm_aic"] = round(float(gmm.aic(X_scaled)), 2)

    return result


if __name__ == "__main__":
    # Test with processed data if present
    data_path = "data/processed/top50_nominal_and_ppp.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        clustered_df = segment_billionaires(df)
        gmm_df = segment_billionaires_gmm(df)
        print("[OK] K-Means Distribution:")
        print(clustered_df["archetype_label"].value_counts())
        print(f"[OK] GMM Model BIC: {gmm_df.attrs.get('gmm_bic')}")
        print(gmm_df[["name", "gmm_label", "gmm_max_prob", "gmm_ambiguity"]].head())

