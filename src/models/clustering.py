"""
UHNWI Wealth Archetype Segmentation Model using K-Means Clustering.
Segments billionaires based on nominal wealth, PPP-adjusted wealth, and PPP uplift.
"""

import os
from typing import Optional, List
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def segment_billionaires(
    df: pd.DataFrame,
    n_clusters: int = 3,
    features: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Apply K-Means clustering to segment billionaires into wealth archetypes.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing billionaire metrics.
    n_clusters : int
        Number of clusters (default: 3).
    features : list of str, optional
        Features to use for clustering.
        
    Returns
    -------
    pd.DataFrame
        Original DataFrame with added 'archetype_cluster' and 'archetype_label' columns.
    """
    result = df.copy()

    # Determine standardized feature names present in DataFrame
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


if __name__ == "__main__":
    # Test with processed data if present
    data_path = "data/processed/top50_nominal_and_ppp.csv"
    if os.path.exists(data_path):
        import os
        df = pd.read_csv(data_path)
        clustered_df = segment_billionaires(df)
        print("[OK] Clustered dataset. Archetype distribution:")
        print(clustered_df["archetype_label"].value_counts())
