"""Build the consolidated Home Credit feature store.

The resulting dataset has one row per ``SK_ID_CURR``.  All source-specific
builders remain responsible for feature engineering; this module only
coordinates them, resolves the bureau/bureau_balance relationship, validates
their outputs, and joins the resulting client-level feature tables.
"""

from __future__ import annotations

import argparse
import gc
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.etl.bureau import build_bureau_features, load_bureau
from src.etl.bureau_balance import (
    build_bureau_balance_features,
    load_bureau_balance,
)
from src.etl.bureau_client_level_features import (
    build_client_level_bureau_features,
)
from src.etl.credit_card_balance import build_credit_card_features
from src.etl.installments_payments import build_installments_features
from src.etl.pos_cash_balance import build_pos_cash_features, load_pos_cash
from src.etl.previous_application import (
    build_previous_application_features,
    load_previous_application,
)
from src.utils.memory_optimization import reduce_memory_usage


ID_COL = "SK_ID_CURR"
BUREAU_ID_COL = "SK_ID_BUREAU"
TARGET_COL = "TARGET"

DEFAULT_SOURCE_FILES = {
    "bureau": "bureau.csv",
    "bureau_balance": "bureau_balance.csv",
    "credit_card_balance": "credit_card_balance.csv",
    "installments_payments": "installments_payments.csv",
    "pos_cash_balance": "POS_CASH_balance.csv",
    "previous_application": "previous_application.csv",
}


def _validate_columns(
    df: pd.DataFrame,
    required_columns: Iterable[str],
    dataset_name: str,
) -> None:
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(
            f"{dataset_name} is missing required columns: {sorted(missing)}"
        )


def _validate_client_features(
    features: pd.DataFrame,
    feature_set_name: str,
) -> None:
    _validate_columns(features, [ID_COL], feature_set_name)

    if features[ID_COL].isna().any():
        raise ValueError(f"{feature_set_name} contains null {ID_COL} values")

    if features[ID_COL].duplicated().any():
        raise ValueError(
            f"{feature_set_name} must contain at most one row per {ID_COL}"
        )


def build_bureau_balance_client_features(
    bureau: pd.DataFrame,
    bureau_balance: pd.DataFrame,
) -> pd.DataFrame:
    """Create client-level features from the bureau_balance loan history."""
    _validate_columns(
        bureau,
        [ID_COL, BUREAU_ID_COL, "DAYS_CREDIT"],
        "bureau",
    )

    balance_features = build_bureau_balance_features(bureau_balance)

    # bureau_balance is loan-level and does not contain SK_ID_CURR.  The bureau
    # table supplies the client relationship and the contract's credit date.
    loan_features = (
        bureau[[ID_COL, BUREAU_ID_COL, "DAYS_CREDIT"]]
        .rename(
            columns={
                "DAYS_CREDIT": "BUREAU_DAYS_CREDIT_MOST_RECENT",
            }
        )
        .merge(
            balance_features,
            on=BUREAU_ID_COL,
            how="left",
            validate="one_to_one",
        )
    )

    client_features = build_client_level_bureau_features(loan_features)
    return reduce_memory_usage(client_features.fillna(0))


def _base_clients(
    feature_frames: Iterable[pd.DataFrame],
    clients: pd.DataFrame | None,
) -> pd.DataFrame:
    if clients is not None:
        _validate_columns(clients, [ID_COL], "clients")
        columns = [ID_COL]
        if TARGET_COL in clients.columns:
            columns.append(TARGET_COL)

        base = clients[columns].copy()
        if base[ID_COL].duplicated().any():
            raise ValueError(f"clients must contain one row per {ID_COL}")
        return base

    id_frames = [frame[[ID_COL]] for frame in feature_frames]
    return (
        pd.concat(id_frames, ignore_index=True)
        .drop_duplicates()
        .sort_values(ID_COL)
        .reset_index(drop=True)
    )


def consolidate_feature_frames(
    feature_frames: Iterable[tuple[str, pd.DataFrame]],
    clients: pd.DataFrame | None = None,
    fill_value: float | None = 0,
) -> pd.DataFrame:
    """Join validated client-level feature tables into one feature store."""
    named_frames = list(feature_frames)
    if not named_frames:
        raise ValueError("At least one feature frame is required")

    for name, frame in named_frames:
        _validate_client_features(frame, name)

    frames = [frame for _, frame in named_frames]
    feature_store = _base_clients(frames, clients)
    known_columns = set(feature_store.columns)
    feature_columns: list[str] = []

    for name, frame in named_frames:
        columns = [column for column in frame.columns if column != ID_COL]
        collisions = known_columns.intersection(columns)
        if collisions:
            raise ValueError(
                f"{name} has columns already present in the feature store: "
                f"{sorted(collisions)}"
            )

        feature_store = feature_store.merge(
            frame,
            on=ID_COL,
            how="left",
            validate="one_to_one",
        )
        known_columns.update(columns)
        feature_columns.extend(columns)

    if fill_value is not None:
        feature_store[feature_columns] = feature_store[feature_columns].fillna(
            fill_value
        )

    return reduce_memory_usage(feature_store)


def build_feature_store(
    bureau: pd.DataFrame,
    bureau_balance: pd.DataFrame,
    credit_card_balance: pd.DataFrame,
    installments_payments: pd.DataFrame,
    pos_cash_balance: pd.DataFrame,
    previous_application: pd.DataFrame,
    clients: pd.DataFrame | None = None,
    fill_value: float | None = 0,
) -> pd.DataFrame:
    """Build all feature sets from in-memory raw DataFrames and consolidate."""
    feature_frames = [
        ("bureau", build_bureau_features(bureau)),
        (
            "bureau_balance_client",
            build_bureau_balance_client_features(bureau, bureau_balance),
        ),
        (
            "credit_card_balance",
            build_credit_card_features(credit_card_balance),
        ),
        (
            "installments_payments",
            build_installments_features(installments_payments),
        ),
        ("pos_cash_balance", build_pos_cash_features(pos_cash_balance)),
        (
            "previous_application",
            build_previous_application_features(previous_application),
        ),
    ]

    return consolidate_feature_frames(
        feature_frames,
        clients=clients,
        fill_value=fill_value,
    )


def _load_csv(path: Path) -> pd.DataFrame:
    return reduce_memory_usage(pd.read_csv(path))


def build_feature_store_from_files(
    data_dir: str | Path,
    application_path: str | Path | None = None,
    fill_value: float | None = 0,
) -> pd.DataFrame:
    """Build features from CSV files while releasing each raw table early."""
    data_dir = Path(data_dir)
    paths = {
        name: data_dir / filename
        for name, filename in DEFAULT_SOURCE_FILES.items()
    }
    missing_files = [str(path) for path in paths.values() if not path.is_file()]
    if missing_files:
        raise FileNotFoundError(
            f"Required source files were not found: {missing_files}"
        )

    clients = None
    if application_path is not None:
        application_path = Path(application_path)
        if not application_path.is_file():
            raise FileNotFoundError(
                f"Application file was not found: {application_path}"
            )
        application = pd.read_csv(
            application_path,
            usecols=lambda column: column in {ID_COL, TARGET_COL},
        )
        clients = reduce_memory_usage(application)

    feature_frames: list[tuple[str, pd.DataFrame]] = []

    bureau = load_bureau(str(paths["bureau"]))
    feature_frames.append(("bureau", build_bureau_features(bureau)))

    bureau_balance = load_bureau_balance(str(paths["bureau_balance"]))
    feature_frames.append(
        (
            "bureau_balance_client",
            build_bureau_balance_client_features(bureau, bureau_balance),
        )
    )
    del bureau, bureau_balance
    gc.collect()

    source_builders = [
        ("credit_card_balance", build_credit_card_features, _load_csv),
        ("installments_payments", build_installments_features, _load_csv),
        ("pos_cash_balance", build_pos_cash_features, load_pos_cash),
        (
            "previous_application",
            build_previous_application_features,
            load_previous_application,
        ),
    ]

    for name, builder, loader in source_builders:
        raw = loader(paths[name]) if loader is _load_csv else loader(str(paths[name]))
        feature_frames.append((name, builder(raw)))
        del raw
        gc.collect()

    return consolidate_feature_frames(
        feature_frames,
        clients=clients,
        fill_value=fill_value,
    )


def save_feature_store(
    feature_store: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """Persist the feature store as CSV or Parquet based on its extension."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    suffix = output_path.suffix.lower()
    if suffix == ".csv":
        feature_store.to_csv(output_path, index=False)
    elif suffix in {".parquet", ".pq"}:
        feature_store.to_parquet(output_path, index=False)
    else:
        raise ValueError("Output path must end in .csv, .parquet, or .pq")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the consolidated Home Credit feature store."
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory containing the source CSV files (default: data).",
    )
    parser.add_argument(
        "--application",
        default="data/application_train.csv",
        help=(
            "Application CSV used as the client base. Its TARGET column is "
            "retained when available (default: data/application_train.csv)."
        ),
    )
    parser.add_argument(
        "--output",
        default="data/feature_store_train.csv",
        help="Output .csv or .parquet path.",
    )
    parser.add_argument(
        "--keep-missing",
        action="store_true",
        help="Keep missing feature values instead of filling them with zero.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    feature_store = build_feature_store_from_files(
        data_dir=args.data_dir,
        application_path=args.application,
        fill_value=None if args.keep_missing else 0,
    )
    save_feature_store(feature_store, args.output)
    print(
        f"Feature store saved to {args.output}: "
        f"{feature_store.shape[0]} rows, {feature_store.shape[1]} columns"
    )


if __name__ == "__main__":
    main()
