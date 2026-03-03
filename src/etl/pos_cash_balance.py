import numpy as np
import pandas as pd

from src.utils.memory_optimization import reduce_memory_usage


ID_COL = "SK_ID_CURR"
PREV_ID_COL = "SK_ID_PREV"

MONTH_COL = "MONTHS_BALANCE"
DPD_COL = "SK_DPD"
DPD_DEF_COL = "SK_DPD_DEF"

CNT_INSTALMENT_COL = "CNT_INSTALMENT"
CNT_INSTALMENT_FUTURE_COL = "CNT_INSTALMENT_FUTURE"

STATUS_COL = "NAME_CONTRACT_STATUS"

RECENT_THRESHOLD = -365  # last 12 months


def load_pos_cash(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return reduce_memory_usage(df)


def _safe_divide(num: pd.Series, den: pd.Series) -> pd.Series:
    den = den.replace(0, np.nan)
    return (num / den).fillna(0)


def build_pos_cash_features(pos: pd.DataFrame) -> pd.DataFrame:
    cols = [
        ID_COL, PREV_ID_COL, MONTH_COL,
        DPD_COL, DPD_DEF_COL,
        CNT_INSTALMENT_COL, CNT_INSTALMENT_FUTURE_COL,
        STATUS_COL
    ]

    df = pos[[c for c in cols if c in pos.columns]].copy()

    # Numeric coercion
    for col in [DPD_COL, DPD_DEF_COL, CNT_INSTALMENT_COL, CNT_INSTALMENT_FUTURE_COL, MONTH_COL]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Flags
    df["__has_dpd"] = (df[DPD_COL] > 0).astype("int8")
    df["__has_dpd_def"] = (df[DPD_DEF_COL] > 0).astype("int8")
    df["__is_recent_1y"] = (df[MONTH_COL] > RECENT_THRESHOLD).astype("int8")

    # Installment progress
    df["__installment_progress"] = _safe_divide(
        df[CNT_INSTALMENT_COL] - df[CNT_INSTALMENT_FUTURE_COL],
        df[CNT_INSTALMENT_COL]
    )

    # Aggregation at customer level
    agg = (
        df.groupby(ID_COL)
        .agg(
            POS_RECORD_COUNT=(MONTH_COL, "count"),

            POS_MONTHS_OLDEST=(MONTH_COL, "min"),
            POS_MONTHS_MOST_RECENT=(MONTH_COL, "max"),

            POS_DPD_MAX=(DPD_COL, "max"),
            POS_DPD_MEAN=(DPD_COL, "mean"),
            POS_DPD_DEF_MAX=(DPD_DEF_COL, "max"),

            POS_DPD_MONTH_COUNT=("__has_dpd", "sum"),
            POS_DPD_DEF_MONTH_COUNT=("__has_dpd_def", "sum"),

            POS_RECENT_1Y_DPD_COUNT=("__has_dpd", lambda x: x[df.loc[x.index, "__is_recent_1y"] == 1].sum()),

            POS_INSTALLMENT_PROGRESS_MEAN=("__installment_progress", "mean"),
        )
        .reset_index()
    )

    # Derived features
    agg["POS_MONTH_SPAN"] = (
        agg["POS_MONTHS_MOST_RECENT"] -
        agg["POS_MONTHS_OLDEST"]
    )

    agg["POS_DPD_RATIO"] = _safe_divide(
        agg["POS_DPD_MONTH_COUNT"],
        agg["POS_RECORD_COUNT"]
    )

    agg["POS_DPD_DEF_RATIO"] = _safe_divide(
        agg["POS_DPD_DEF_MONTH_COUNT"],
        agg["POS_RECORD_COUNT"]
    )

    agg["POS_RECENT_1Y_DPD_RATIO"] = _safe_divide(
        agg["POS_RECENT_1Y_DPD_COUNT"],
        agg["POS_RECORD_COUNT"]
    )

    agg["POS_HAS_DPD_FLAG"] = (agg["POS_DPD_MAX"] > 0).astype("int8")

    # Cleanup
    agg = agg.drop(columns=[
        "POS_DPD_MONTH_COUNT",
        "POS_DPD_DEF_MONTH_COUNT",
        "POS_RECENT_1Y_DPD_COUNT"
    ])

    return reduce_memory_usage(agg.fillna(0))


if __name__ == "__main__":
    pos_df = load_pos_cash("data/POS_CASH_balance.csv")
    features = build_pos_cash_features(pos_df)
    print(features.shape)
    print(features.head())