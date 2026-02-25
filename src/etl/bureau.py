import numpy as np
import pandas as pd

from src.utils.memory_optimization import reduce_memory_usage


ID_COL = "SK_ID_CURR"
BUREAU_ID_COL = "SK_ID_BUREAU"

ACTIVE_COL = "CREDIT_ACTIVE"
ACTIVE_VALUE = "Active"
CLOSED_VALUE = "Closed"

DAYS_CREDIT_COL = "DAYS_CREDIT"

DEBT_COL = "AMT_CREDIT_SUM_DEBT"
CREDIT_SUM_COL = "AMT_CREDIT_SUM"
MAX_OVERDUE_COL = "AMT_CREDIT_MAX_OVERDUE"

RECENT_THRESHOLD = -365  # last 12 months


def load_bureau(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return reduce_memory_usage(df)


def _safe_divide(num: pd.Series, den: pd.Series) -> pd.Series:
    den = den.replace(0, np.nan)
    return (num / den).fillna(0)


def build_bureau_features(bureau: pd.DataFrame) -> pd.DataFrame:
    b = bureau.copy()

    # Ensure numeric
    for col in [DEBT_COL, CREDIT_SUM_COL, MAX_OVERDUE_COL, DAYS_CREDIT_COL]:
        b[col] = pd.to_numeric(b[col], errors="coerce")

    # Flags
    b["__is_active"] = (b[ACTIVE_COL] == ACTIVE_VALUE).astype("int8")
    b["__is_closed"] = (b[ACTIVE_COL] == CLOSED_VALUE).astype("int8")
    b["__has_overdue"] = (b[MAX_OVERDUE_COL].fillna(0) > 0).astype("int8")
    b["__is_recent_1y"] = (b[DAYS_CREDIT_COL] > RECENT_THRESHOLD).astype("int8")

    active = b[b["__is_active"] == 1]
    recent = b[b["__is_recent_1y"] == 1]

    # 1Total loan count
    total_loans = (
        b.groupby(ID_COL)[BUREAU_ID_COL]
        .nunique()
        .rename("BUREAU_TOTAL_LOAN_COUNT")
        .reset_index()
    )

    # 2 Active / Closed counts + ratio
    active_closed = (
        b.groupby(ID_COL)[["__is_active", "__is_closed"]]
        .sum()
        .rename(columns={
            "__is_active": "BUREAU_ACTIVE_LOAN_COUNT",
            "__is_closed": "BUREAU_CLOSED_LOAN_COUNT",
        })
        .reset_index()
    )

    active_closed["BUREAU_ACTIVE_LOAN_RATIO"] = _safe_divide(
        active_closed["BUREAU_ACTIVE_LOAN_COUNT"],
        active_closed["BUREAU_ACTIVE_LOAN_COUNT"] +
        active_closed["BUREAU_CLOSED_LOAN_COUNT"]
    )

    # 3 Credit recency & span
    credit_age = (
        b.groupby(ID_COL)[DAYS_CREDIT_COL]
        .agg(["max", "min"])
        .reset_index()
        .rename(columns={
            "max": "BUREAU_DAYS_CREDIT_MOST_RECENT",
            "min": "BUREAU_DAYS_CREDIT_OLDEST",
        })
    )

    credit_age["BUREAU_DAYS_CREDIT_SPAN"] = (
        credit_age["BUREAU_DAYS_CREDIT_MOST_RECENT"] -
        credit_age["BUREAU_DAYS_CREDIT_OLDEST"]
    )

    #  4 Overdue ratio
    overdue_ratio = (
        b.groupby(ID_COL)["__has_overdue"]
        .mean()
        .rename("BUREAU_OVERDUE_LOAN_RATIO")
        .reset_index()
    )

    # 5 Active monetary aggregates + debt ratio
    active_amounts = (
        active.groupby(ID_COL)[[DEBT_COL, CREDIT_SUM_COL]]
        .sum(min_count=1)
        .reset_index()
        .rename(columns={
            DEBT_COL: "BUREAU_ACTIVE_AMT_CREDIT_SUM_DEBT_SUM",
            CREDIT_SUM_COL: "BUREAU_ACTIVE_AMT_CREDIT_SUM_SUM",
        })
    )

    active_amounts["BUREAU_ACTIVE_DEBT_RATIO"] = _safe_divide(
        active_amounts["BUREAU_ACTIVE_AMT_CREDIT_SUM_DEBT_SUM"],
        active_amounts["BUREAU_ACTIVE_AMT_CREDIT_SUM_SUM"],
    )

    # 6 Active overdue max
    active_overdue = (
        active.groupby(ID_COL)[MAX_OVERDUE_COL]
        .max()
        .rename("BUREAU_ACTIVE_AMT_CREDIT_MAX_OVERDUE_MAX")
        .reset_index()
    )

    # 7 Recent 1Y loan count
    recent_loans = (
        recent.groupby(ID_COL)[BUREAU_ID_COL]
        .nunique()
        .rename("BUREAU_RECENT_1Y_LOAN_COUNT")
        .reset_index()
    )

    # Merge everything
    frames = [
        total_loans,
        active_closed,
        credit_age,
        overdue_ratio,
        active_amounts,
        active_overdue,
        recent_loans,
    ]

    final = frames[0]
    for df in frames[1:]:
        final = final.merge(df, on=ID_COL, how="left")

    return reduce_memory_usage(final.fillna(0))


if __name__ == "__main__":
    bureau_df = load_bureau("data/bureau.csv")
    features = build_bureau_features(bureau_df)
    print(features.shape)
    print(features.head())