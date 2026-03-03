from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.memory_optimization import reduce_memory_usage

RECENT_WINDOW_DAYS = 90
EPS = 1e-9


def _safe_div(numer: pd.Series, denom: pd.Series, eps: float = EPS) -> pd.Series:
    """Elementwise safe division to avoid division by zero."""
    return numer / (denom.replace(0, np.nan) + eps)


def _slope(x: np.ndarray, y: np.ndarray) -> float:
    """
    Computes slope of y ~ a*x + b (linear trend).
    Returns 0.0 if not enough data or degenerate x.
    """
    if len(x) < 2:
        return 0.0
    if np.nanstd(x) < 1e-12:
        return 0.0
    # Drop NaNs
    m = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[m], y[m]
    if len(x) < 2:
        return 0.0
    a, _b = np.polyfit(x, y, 1)
    return float(a)


def build_installments_features(installments: pd.DataFrame) -> pd.DataFrame:
    """
    Build 10 must-have features from installment_payments.

    Returns
    -------
    pd.DataFrame
        Columns:
          SK_ID_CURR,
          INST_DPD_MEAN,
          INST_DPD_MAX,
          INST_LATE_RATIO,
          INST_DPD_30_RATIO,
          INST_PAYMENT_RATIO_MEAN,
          INST_PAYMENT_RATIO_MIN,
          INST_LOW_PAYMENT_RATIO,
          INST_RECENT_DPD_MEAN_90D,
          INST_RECENT_LATE_RATIO_90D,
          INST_DPD_TREND
    """
    needed = {
        "SK_ID_CURR", "SK_ID_PREV",
        "DAYS_INSTALMENT", "DAYS_ENTRY_PAYMENT",
        "AMT_INSTALMENT", "AMT_PAYMENT",
    }
    missing = needed - set(installments.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = installments.copy()

    # --- Row-level signals ---
    # DPD (days past due): positive only
    df["DPD"] = (df["DAYS_ENTRY_PAYMENT"] - df["DAYS_INSTALMENT"]).clip(lower=0)

    # Payment ratio and underpayment flag
    df["PAYMENT_RATIO"] = _safe_div(df["AMT_PAYMENT"], df["AMT_INSTALMENT"]).clip(lower=0)
    df["IS_LATE"] = (df["DPD"] > 0).astype(int)
    df["IS_DPD_30"] = (df["DPD"] > 30).astype(int)
    df["IS_LOW_PAYMENT"] = (df["AMT_PAYMENT"] + EPS < df["AMT_INSTALMENT"]).astype(int)

    # Recent window (last 90 days in the dataset timeline, closer to 0 is more recent)
    df["IS_RECENT_90D"] = (df["DAYS_INSTALMENT"] >= -RECENT_WINDOW_DAYS).astype(int)

    # --- Aggregations by customer ---
    g = df.groupby("SK_ID_CURR", as_index=False)

    agg_core = g.agg(
        INST_DPD_MEAN=("DPD", "mean"),
        INST_DPD_MAX=("DPD", "max"),
        INST_LATE_RATIO=("IS_LATE", "mean"),
        INST_DPD_30_RATIO=("IS_DPD_30", "mean"),
        INST_PAYMENT_RATIO_MEAN=("PAYMENT_RATIO", "mean"),
        INST_PAYMENT_RATIO_MIN=("PAYMENT_RATIO", "min"),
        INST_LOW_PAYMENT_RATIO=("IS_LOW_PAYMENT", "mean"),
    )

    # Recent-only aggregations (handle customers with no recent rows)
    df_recent = df[df["IS_RECENT_90D"] == 1].copy()
    if df_recent.empty:
        recent = pd.DataFrame({"SK_ID_CURR": agg_core["SK_ID_CURR"].values})
        recent["INST_RECENT_DPD_MEAN_90D"] = 0.0
        recent["INST_RECENT_LATE_RATIO_90D"] = 0.0
    else:
        gr = df_recent.groupby("SK_ID_CURR", as_index=False).agg(
            INST_RECENT_DPD_MEAN_90D=("DPD", "mean"),
            INST_RECENT_LATE_RATIO_90D=("IS_LATE", "mean"),
        )
        recent = pd.DataFrame({"SK_ID_CURR": agg_core["SK_ID_CURR"].values}).merge(
            gr, on="SK_ID_CURR", how="left"
        )
        recent["INST_RECENT_DPD_MEAN_90D"] = recent["INST_RECENT_DPD_MEAN_90D"].fillna(0.0)
        recent["INST_RECENT_LATE_RATIO_90D"] = recent["INST_RECENT_LATE_RATIO_90D"].fillna(0.0)

    # Trend of DPD over time (per customer)
    # Use DAYS_INSTALMENT as time axis (more negative = older). Slope > 0 means DPD worsening as time moves toward 0.
    def _dpd_trend(sub: pd.DataFrame) -> float:
        sub = sub.sort_values("DAYS_INSTALMENT")
        x = sub["DAYS_INSTALMENT"].to_numpy(dtype=float)
        y = sub["DPD"].to_numpy(dtype=float)
        return _slope(x, y)

    trend = (
        df.groupby("SK_ID_CURR", as_index=False)
          .apply(_dpd_trend)
          .reset_index()
          .rename(columns={0: "INST_DPD_TREND"})
    )

    # --- Final dataset ---
    out = (
        agg_core
        .merge(recent, on="SK_ID_CURR", how="left")
        .merge(trend, on="SK_ID_CURR", how="left")
    )

    # Clean up any remaining NaNs
    for c in out.columns:
        if c != "SK_ID_CURR":
            out[c] = out[c].fillna(0.0)

    return reduce_memory_usage(out)


if __name__ == "__main__":
    # Example usage (adapt paths to your project)
    path = "data/installments_payments.csv"
    inst = reduce_memory_usage(pd.read_csv(path))
    feats = reduce_memory_usage(build_installments_features(inst))
    print(feats.head())