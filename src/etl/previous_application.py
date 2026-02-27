import numpy as np
import pandas as pd

from src.utils.memory_optimization import reduce_memory_usage


ID_COL = "SK_ID_CURR"
PREV_ID_COL = "SK_ID_PREV"

STATUS_COL = "NAME_CONTRACT_STATUS"
APPROVED = "Approved"
REFUSED = "Refused"

DAYS_DECISION_COL = "DAYS_DECISION"  # negative days before current application

AMT_APPLICATION_COL = "AMT_APPLICATION"
AMT_CREDIT_COL = "AMT_CREDIT"
AMT_ANNUITY_COL = "AMT_ANNUITY"
AMT_DOWN_PAYMENT_COL = "AMT_DOWN_PAYMENT"
CNT_PAYMENT_COL = "CNT_PAYMENT"

RECENT_THRESHOLD = -365  # last 12 months


def load_previous_application(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return reduce_memory_usage(df)


def _safe_divide(num: pd.Series, den: pd.Series) -> pd.Series:
    den = den.replace(0, np.nan)
    return (num / den).fillna(0)


def build_previous_application_features(prev: pd.DataFrame) -> pd.DataFrame:
    # Keep only needed columns (faster + less memory)
    cols = [
        ID_COL, PREV_ID_COL, STATUS_COL, DAYS_DECISION_COL,
        AMT_APPLICATION_COL, AMT_CREDIT_COL, AMT_ANNUITY_COL,
        AMT_DOWN_PAYMENT_COL, CNT_PAYMENT_COL
    ]
    df = prev[[c for c in cols if c in prev.columns]].copy()

    # Numeric coercion
    for col in [
        DAYS_DECISION_COL, AMT_APPLICATION_COL, AMT_CREDIT_COL,
        AMT_ANNUITY_COL, AMT_DOWN_PAYMENT_COL, CNT_PAYMENT_COL
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Flags
    df["__is_approved"] = (df[STATUS_COL] == APPROVED).astype("int8")
    df["__is_refused"] = (df[STATUS_COL] == REFUSED).astype("int8")
    df["__is_recent_1y"] = (df[DAYS_DECISION_COL] > RECENT_THRESHOLD).astype("int8")

    # Ratios per application row (later aggregated)
    # credit_to_application: how much granted vs requested (bank haircut signal)
    df["__credit_to_app_ratio"] = _safe_divide(df[AMT_CREDIT_COL], df[AMT_APPLICATION_COL])
    df["__credit_minus_app"] = (df[AMT_CREDIT_COL] - df[AMT_APPLICATION_COL])

    # Base aggregation at customer level
    agg = (
        df.groupby(ID_COL)
        .agg(
            PREV_APP_COUNT=(PREV_ID_COL, "nunique"),
            PREV_APPROVED_COUNT=("__is_approved", "sum"),
            PREV_REFUSED_COUNT=("__is_refused", "sum"),

            PREV_DAYS_DECISION_MOST_RECENT=(DAYS_DECISION_COL, "max"),
            PREV_DAYS_DECISION_OLDEST=(DAYS_DECISION_COL, "min"),

            PREV_LAST_1Y_APP_COUNT=("__is_recent_1y", "sum"),

            PREV_AMT_CREDIT_MEAN=(AMT_CREDIT_COL, "mean"),
            PREV_AMT_CREDIT_MAX=(AMT_CREDIT_COL, "max"),
            PREV_AMT_APPLICATION_MEAN=(AMT_APPLICATION_COL, "mean"),
            PREV_AMT_ANNUITY_MEAN=(AMT_ANNUITY_COL, "mean"),

            PREV_CNT_PAYMENT_MEAN=(CNT_PAYMENT_COL, "mean"),
            PREV_CNT_PAYMENT_MAX=(CNT_PAYMENT_COL, "max"),

            PREV_CREDIT_TO_APPLICATION_RATIO_MEAN=("__credit_to_app_ratio", "mean"),
            PREV_CREDIT_MINUS_APPLICATION_MEAN=("__credit_minus_app", "mean"),
        )
        .reset_index()
    )

    # Derived features
    agg["PREV_APPROVAL_RATIO"] = _safe_divide(agg["PREV_APPROVED_COUNT"], agg["PREV_APP_COUNT"])
    agg["PREV_REFUSED_RATIO"] = _safe_divide(agg["PREV_REFUSED_COUNT"], agg["PREV_APP_COUNT"])

    agg["PREV_HAS_REFUSED_FLAG"] = (agg["PREV_REFUSED_COUNT"] > 0).astype("int8")

    # Span of history (length of relationship in decision-time space)
    agg["PREV_DAYS_DECISION_SPAN"] = (
        agg["PREV_DAYS_DECISION_MOST_RECENT"] - agg["PREV_DAYS_DECISION_OLDEST"]
    )

    # Fill NaNs: for customers without any previous applications, they won't appear here.
    # Use LEFT JOIN later with application table; filling here is fine.
    agg = agg.fillna(0)

    return reduce_memory_usage(agg)


if __name__ == "__main__":
    prev_df = load_previous_application("data/previous_application.csv")
    features = build_previous_application_features(prev_df)
    print(features.shape)
    print(features.head())