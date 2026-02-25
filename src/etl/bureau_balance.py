from functools import reduce
import pandas as pd
from src.utils.memory_optimization import reduce_memory_usage

BUREAU_ID_COL = "SK_ID_BUREAU"
MONTH_COL = "MONTHS_BALANCE"
STATUS_COL = "STATUS"


def load_bureau_balance(path: str) -> pd.DataFrame:
    bureau_balance = reduce_memory_usage(pd.read_csv(path))
    print(f"Number of observations: {bureau_balance.shape[0]}")
    print(f"Number of features: {bureau_balance.shape[1]}")
    return bureau_balance


def build_loan_record_count(bureau_balance: pd.DataFrame) -> pd.DataFrame:
    return (
        bureau_balance.groupby(by=BUREAU_ID_COL)
        .count()
        .reset_index()[[BUREAU_ID_COL, MONTH_COL]]
        .rename(columns={MONTH_COL: "BUREAU_BALANCE_RECORD_COUNT"})
    )


def build_loan_time_window_features(bureau_balance: pd.DataFrame) -> pd.DataFrame:
    features = (
        bureau_balance.groupby(by=BUREAU_ID_COL)[MONTH_COL]
        .agg(["min", "max"])
        .reset_index()
        .rename(
            columns={
                "min": "BUREAU_BALANCE_OLDEST_MONTH",
                "max": "BUREAU_BALANCE_MOST_RECENT_MONTH",
            }
        )
    )
    features["BUREAU_BALANCE_MONTH_SPAN"] = (
        features["BUREAU_BALANCE_MOST_RECENT_MONTH"]
        - features["BUREAU_BALANCE_OLDEST_MONTH"]
    )
    return features


def build_loan_status_count_features(bureau_balance: pd.DataFrame) -> pd.DataFrame:
    status_counts = (
        bureau_balance.pivot_table(
            index=BUREAU_ID_COL,
            columns=STATUS_COL,
            values=MONTH_COL,
            aggfunc="count",
            fill_value=0,
        )
        .rename(columns=lambda status: f"BUREAU_BALANCE_STATUS_{status}_COUNT")
        .reset_index()
    )
    return status_counts


def build_loan_status_ratio_features(status_counts: pd.DataFrame) -> pd.DataFrame:
    ratio_features = status_counts[[BUREAU_ID_COL]].copy()
    count_cols = [col for col in status_counts.columns if col.endswith("_COUNT")]
    total = status_counts[count_cols].sum(axis=1)
    for col in count_cols:
        ratio_col = col.replace("_COUNT", "_RATIO")
        ratio_features[ratio_col] = status_counts[col] / total.where(total > 0, 1)
    return ratio_features


def build_loan_delinquency_features(bureau_balance: pd.DataFrame) -> pd.DataFrame:
    delinquency = bureau_balance[[BUREAU_ID_COL, STATUS_COL]].copy()
    delinquency["STATUS_NUMERIC"] = pd.to_numeric(
        delinquency[STATUS_COL], errors="coerce"
    )
    delinquency = delinquency.dropna(subset=["STATUS_NUMERIC"])
    delinquency["STATUS_NUMERIC"] = delinquency["STATUS_NUMERIC"].astype("int8")
    delinquency["HAS_DPD"] = (delinquency["STATUS_NUMERIC"] > 0).astype("int8")

    return (
        delinquency.groupby(by=BUREAU_ID_COL)[["STATUS_NUMERIC", "HAS_DPD"]]
        .agg({"STATUS_NUMERIC": ["max", "mean"], "HAS_DPD": "max"})
        .reset_index()
        .set_axis(
            [
                BUREAU_ID_COL,
                "BUREAU_BALANCE_DPD_MAX",
                "BUREAU_BALANCE_DPD_MEAN",
                "BUREAU_BALANCE_HAS_DPD",
            ],
            axis=1,
        )
    )


def build_loan_recent_status_features(bureau_balance: pd.DataFrame) -> pd.DataFrame:
    recent_status = (
        bureau_balance.loc[
            bureau_balance.groupby(by=BUREAU_ID_COL)[MONTH_COL].idxmax(),
            [BUREAU_ID_COL, STATUS_COL],
        ]
        .copy()
        .reset_index(drop=True)
    )
    recent_status = pd.concat(
        [
            recent_status[[BUREAU_ID_COL]],
            pd.get_dummies(recent_status[STATUS_COL], prefix="BUREAU_BALANCE_RECENT_STATUS"),
        ],
        axis=1,
    )
    return recent_status


def build_loan_level_features(bureau_balance: pd.DataFrame) -> pd.DataFrame:
    status_counts = build_loan_status_count_features(bureau_balance)
    base = build_loan_record_count(bureau_balance)
    feature_frames = [
        build_loan_time_window_features(bureau_balance),
        status_counts,
        build_loan_status_ratio_features(status_counts),
        build_loan_delinquency_features(bureau_balance),
        build_loan_recent_status_features(bureau_balance),
    ]
    return reduce(
        lambda left, right: left.merge(right, on=BUREAU_ID_COL, how="left"),
        feature_frames,
        base,
    ).fillna(0)


def build_bureau_balance_features(bureau_balance: pd.DataFrame) -> pd.DataFrame:
    return build_loan_level_features(bureau_balance)


if __name__ == "__main__":
    bureau_balance_df = load_bureau_balance("data/bureau_balance.csv")
    features = build_bureau_balance_features(bureau_balance_df)
    print(features.head())
