from functools import reduce
import pandas as pd
import numpy as np
from src.utils.memory_optimization import reduce_memory_usage

BUREAU_ID_COL = "SK_ID_BUREAU"
MONTH_COL = "MONTHS_BALANCE"
STATUS_COL = "STATUS"


def load_bureau_balance(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return reduce_memory_usage(df)


def build_bureau_balance_features(bureau_balance: pd.DataFrame) -> pd.DataFrame:
    df = bureau_balance[[BUREAU_ID_COL, MONTH_COL, STATUS_COL]].copy()

    # Convert STATUS to numeric when possible (0–5 represent DPD levels)
    df["STATUS_NUMERIC"] = pd.to_numeric(df[STATUS_COL], errors="coerce")

    # Flag months with positive DPD
    df["HAS_POSITIVE_DPD_MONTH"] = (df["STATUS_NUMERIC"] > 0).astype("int8")

    # Core aggregation
    agg = (
        df.groupby(BUREAU_ID_COL)
        .agg(
            BUREAU_BALANCE_RECORD_COUNT=(MONTH_COL, "count"),
            BUREAU_BALANCE_OLDEST_MONTH=(MONTH_COL, "min"),
            BUREAU_BALANCE_MOST_RECENT_MONTH=(MONTH_COL, "max"),
            BUREAU_BALANCE_DPD_MAX=("STATUS_NUMERIC", "max"),
            BUREAU_BALANCE_DPD_MONTH_COUNT=("HAS_POSITIVE_DPD_MONTH", "sum"),
        )
        .reset_index()
    )

    # Duration of loan history
    agg["BUREAU_BALANCE_MONTH_SPAN"] = (
        agg["BUREAU_BALANCE_MOST_RECENT_MONTH"]
        - agg["BUREAU_BALANCE_OLDEST_MONTH"]
    )

    # Frequency of months with positive DPD
    agg["BUREAU_BALANCE_DPD_RATIO"] = (
        agg["BUREAU_BALANCE_DPD_MONTH_COUNT"]
        / agg["BUREAU_BALANCE_RECORD_COUNT"].replace(0, np.nan)
    ).fillna(0)

    # Binary indicator of any positive DPD
    agg["BUREAU_BALANCE_HAS_POSITIVE_DPD"] = (
        agg["BUREAU_BALANCE_DPD_MAX"] > 0
    ).astype("int8")

    # Remove intermediate column
    agg = agg.drop(columns=["BUREAU_BALANCE_DPD_MONTH_COUNT"])

    return reduce_memory_usage(agg.fillna(0))


if __name__ == "__main__":
    bureau_balance_df = load_bureau_balance("data/bureau_balance.csv")
    features = build_bureau_balance_features(bureau_balance_df)
    print(features.shape)
    print(features.head())
