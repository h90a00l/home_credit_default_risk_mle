"""
Feature Engineering - credit_card_balance.csv (Home Credit)

Output:
    One row per SK_ID_CURR with 10 must-have credit card behavior features.

Assumptions:
    - Input dataframe has columns:
        SK_ID_CURR, SK_ID_PREV, MONTHS_BALANCE,
        AMT_BALANCE, AMT_CREDIT_LIMIT_ACTUAL,
        AMT_PAYMENT_TOTAL_CURRENT,
        AMT_DRAWINGS_CURRENT,
        SK_DPD
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.memory_optimization import reduce_memory_usage

RECENT_WINDOW_MONTHS = 3
EPS = 1e-9


def _safe_div(numer: pd.Series, denom: pd.Series, eps: float = EPS) -> pd.Series:
    """Safe elementwise division to avoid division by zero."""
    return numer / (denom.replace(0, np.nan) + eps)


def _slope(x: np.ndarray, y: np.ndarray) -> float:
    """
    Computes slope of y ~ a*x + b.
    Returns 0.0 if there are fewer than 2 valid points
    or if x has no variation.
    """
    mask = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[mask], y[mask]

    if len(x) < 2:
        return 0.0
    if np.nanstd(x) < 1e-12:
        return 0.0

    a, _b = np.polyfit(x, y, 1)
    return float(a)


def build_credit_card_features(credit_card: pd.DataFrame) -> pd.DataFrame:
    """
    Build 10 must-have features from credit_card_balance.csv.

    Returns
    -------
    pd.DataFrame
        Columns:
          SK_ID_CURR,
          CC_UTIL_MEAN,
          CC_UTIL_MAX,
          CC_PAYMENT_RATIO_MEAN,
          CC_LOW_PAYMENT_RATIO,
          CC_DPD_MEAN,
          CC_DPD_MAX,
          CC_ACTIVE_RATIO,
          CC_DRAWINGS_MEAN,
          CC_RECENT_UTIL_MEAN_3M,
          CC_BALANCE_TREND
    """
    needed = {
        "SK_ID_CURR",
        "SK_ID_PREV",
        "MONTHS_BALANCE",
        "AMT_BALANCE",
        "AMT_CREDIT_LIMIT_ACTUAL",
        "AMT_PAYMENT_TOTAL_CURRENT",
        "AMT_DRAWINGS_CURRENT",
        "SK_DPD",
    }
    missing = needed - set(credit_card.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = credit_card.copy()

    # ------------------------------------------------------------------
    # Row-level variables
    # ------------------------------------------------------------------
    df["UTILIZATION"] = _safe_div(df["AMT_BALANCE"], df["AMT_CREDIT_LIMIT_ACTUAL"]).clip(lower=0)
    df["PAYMENT_RATIO"] = _safe_div(df["AMT_PAYMENT_TOTAL_CURRENT"], df["AMT_BALANCE"]).clip(lower=0)

    df["IS_LOW_PAYMENT"] = (
        df["AMT_PAYMENT_TOTAL_CURRENT"] + EPS < df["AMT_BALANCE"]
    ).astype(int)

    df["IS_ACTIVE"] = (df["AMT_BALANCE"] > 0).astype(int)

    df["IS_RECENT_3M"] = (df["MONTHS_BALANCE"] >= -RECENT_WINDOW_MONTHS).astype(int)

    # ------------------------------------------------------------------
    # Main customer-level aggregations
    # ------------------------------------------------------------------
    agg_core = (
        df.groupby("SK_ID_CURR", as_index=False)
        .agg(
            CC_UTIL_MEAN=("UTILIZATION", "mean"),
            CC_UTIL_MAX=("UTILIZATION", "max"),
            CC_PAYMENT_RATIO_MEAN=("PAYMENT_RATIO", "mean"),
            CC_LOW_PAYMENT_RATIO=("IS_LOW_PAYMENT", "mean"),
            CC_DPD_MEAN=("SK_DPD", "mean"),
            CC_DPD_MAX=("SK_DPD", "max"),
            CC_ACTIVE_RATIO=("IS_ACTIVE", "mean"),
            CC_DRAWINGS_MEAN=("AMT_DRAWINGS_CURRENT", "mean"),
        )
    )

    # ------------------------------------------------------------------
    # Recent utilization (last 3 months)
    # ------------------------------------------------------------------
    df_recent = df[df["IS_RECENT_3M"] == 1].copy()

    if df_recent.empty:
        recent = pd.DataFrame({"SK_ID_CURR": agg_core["SK_ID_CURR"].values})
        recent["CC_RECENT_UTIL_MEAN_3M"] = 0.0
    else:
        recent_agg = (
            df_recent.groupby("SK_ID_CURR", as_index=False)
            .agg(CC_RECENT_UTIL_MEAN_3M=("UTILIZATION", "mean"))
        )

        recent = pd.DataFrame({"SK_ID_CURR": agg_core["SK_ID_CURR"].values}).merge(
            recent_agg,
            on="SK_ID_CURR",
            how="left",
        )
        recent["CC_RECENT_UTIL_MEAN_3M"] = recent["CC_RECENT_UTIL_MEAN_3M"].fillna(0.0)

    # ------------------------------------------------------------------
    # Balance trend over time
    # MONTHS_BALANCE goes from older negative values toward 0
    # Positive slope => balance increasing as time moves toward present
    # ------------------------------------------------------------------
    def _balance_trend(sub: pd.DataFrame) -> float:
        sub = sub.sort_values("MONTHS_BALANCE")
        x = sub["MONTHS_BALANCE"].to_numpy(dtype=float)
        y = sub["AMT_BALANCE"].to_numpy(dtype=float)
        return _slope(x, y)

    trend = (
        df.groupby("SK_ID_CURR")
        .apply(_balance_trend)
        .reset_index(name="CC_BALANCE_TREND")
    )

    # ------------------------------------------------------------------
    # Final output
    # ------------------------------------------------------------------
    out = (
        agg_core
        .merge(recent, on="SK_ID_CURR", how="left")
        .merge(trend, on="SK_ID_CURR", how="left")
    )

    for col in out.columns:
        if col != "SK_ID_CURR":
            out[col] = out[col].fillna(0.0)

    return out


if __name__ == "__main__":
    
    path = "data/credit_card_balance.csv"
    inst = reduce_memory_usage(pd.read_csv(path))
    feats = reduce_memory_usage(build_credit_card_features(inst))
    print(feats.head())
