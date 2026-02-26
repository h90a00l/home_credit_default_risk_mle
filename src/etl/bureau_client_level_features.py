import pandas as pd
import numpy as np


def build_client_level_bureau_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates bureau + bureau_balance features to client level (SK_ID_CURR).
    """

    agg_dict = {
        "SK_ID_BUREAU": ["count"],
        "BUREAU_BALANCE_DPD_MAX": ["max", "mean"],
        "BUREAU_BALANCE_DPD_RATIO": ["mean", "max"],
        "BUREAU_BALANCE_HAS_POSITIVE_DPD": ["sum", "mean"],
        "BUREAU_BALANCE_MONTH_SPAN": ["mean", "max"],
        "BUREAU_DAYS_CREDIT_MOST_RECENT": ["max", "min"],
        'BUREAU_BALANCE_OLDEST_MONTH': ["max", "min"],
        'BUREAU_BALANCE_MOST_RECENT_MONTH': ["max", "min"],
    }

    client_agg = (
        df
        .groupby("SK_ID_CURR")
        .agg(agg_dict)
    )

    client_agg.columns = [
        f"{col}_{stat}".upper() for col, stat in client_agg.columns
    ]

    client_agg = client_agg.reset_index()

    # Weighted DPD ratio
    weighted_dpd = (
        df.assign(
            weighted_dpd=lambda x:
                x["BUREAU_BALANCE_DPD_RATIO"] *
                x["BUREAU_BALANCE_MONTH_SPAN"]
        )
        .groupby("SK_ID_CURR")
        .agg(
            total_weighted_dpd=("weighted_dpd", "sum"),
            total_month_span=("BUREAU_BALANCE_MONTH_SPAN", "sum")
        )
        .reset_index()
    )

    weighted_dpd["BUREAU_BALANCE_DPD_RATIO_WEIGHTED_MEAN"] = (
        weighted_dpd["total_weighted_dpd"] /
        weighted_dpd["total_month_span"].replace(0, np.nan)
    )

    weighted_dpd = weighted_dpd[
        ["SK_ID_CURR", "BUREAU_BALANCE_DPD_RATIO_WEIGHTED_MEAN"]
    ]

    # Recent DPD flag (past 3 months)
    recent_dpd = (
        df.assign(
            has_recent_dpd=lambda x:
                np.where(
                    (x["BUREAU_DAYS_CREDIT_MOST_RECENT"] >= -3) &
                    (x["BUREAU_BALANCE_DPD_MAX"] > 0),
                    1,
                    0
                )
        )
        .groupby("SK_ID_CURR")
        .agg(HAS_RECENT_DPD=("has_recent_dpd", "max"))
        .reset_index()
    )

    client_features = (
        client_agg
        .merge(weighted_dpd, on="SK_ID_CURR", how="left")
        .merge(recent_dpd, on="SK_ID_CURR", how="left")
    )

    return client_features


# =====================================================
# Main block for testing
# =====================================================
if __name__ == "__main__":

    # -------------------------
    # Create synthetic test data
    # -------------------------
    np.random.seed(42)

    test_df = pd.DataFrame({
        "SK_ID_CURR": [100001, 100001, 100001,
                       100002, 100002,
                       100003],
        "SK_ID_BUREAU": [1, 2, 3, 4, 5, 6],
        "BUREAU_BALANCE_DPD_MAX": [0, 1, 0, 2, 0, 0],
        "BUREAU_BALANCE_DPD_RATIO": [0.0, 0.02, 0.0, 0.10, 0.0, 0.0],
        "BUREAU_BALANCE_HAS_POSITIVE_DPD": [0, 1, 0, 1, 0, 0],
        "BUREAU_BALANCE_MONTH_SPAN": [12, 52, 24, 36, 18, 60],
        "BUREAU_DAYS_CREDIT_MOST_RECENT": [0, -2, -10, -1, -5, -40],
        'BUREAU_BALANCE_OLDEST_MONTH': [0, -2, -10, -1, -5, -40],
        'BUREAU_BALANCE_MOST_RECENT_MONTH': [0, -2, -10, -1, -5, -40],
    })

    print("=== Loan-level dataset ===")
    print(test_df)
    print()

    # -------------------------
    # Run aggregation
    # -------------------------
    client_features = build_client_level_bureau_features(test_df)

    print("=== Client-level features ===")
    print(client_features)
    print()

    # -------------------------
    # Basic validation checks
    # -------------------------
    print("=== Sanity checks ===")
    print(f"Number of clients: {client_features['SK_ID_CURR'].nunique()}")
    print("Columns generated:")
    print(client_features.columns.tolist())