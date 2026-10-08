from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


RANDOM_STATE = 42
TEST_SIZE = 0.20

DATA_DIR = Path("data")

FEATURE_STORE_PATH = DATA_DIR / "feature_store_train.parquet"
SPLIT_PATH = DATA_DIR / "split_assignment.parquet"


def create_split_assignment(
    feature_store_path: Path,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    """
    Create a stratified development/test split based on TARGET.

    Only SK_ID_CURR and TARGET are loaded from the feature store.
    The returned DataFrame contains the client identifier and its
    assigned split.
    """

    df = pd.read_parquet(
        feature_store_path,
        columns=["SK_ID_CURR", "TARGET"],
    )

    if df["SK_ID_CURR"].duplicated().any():
        raise ValueError("SK_ID_CURR must be unique in the feature store.")

    if df["TARGET"].isna().any():
        raise ValueError("TARGET contains missing values.")

    development, test = train_test_split(
        df,
        test_size=test_size,
        stratify=df["TARGET"],
        random_state=random_state,
    )

    development = development[["SK_ID_CURR"]].copy()
    development["SPLIT"] = "development"

    test = test[["SK_ID_CURR"]].copy()
    test["SPLIT"] = "test"

    split_assignment = pd.concat(
        [development, test],
        ignore_index=True,
    )

    return split_assignment


def validate_split(
    split_assignment: pd.DataFrame,
    feature_store_path: Path,
) -> None:
    """Validate split integrity and display basic statistics."""

    target = pd.read_parquet(
        feature_store_path,
        columns=["SK_ID_CURR", "TARGET"],
    )

    split_summary = (
        split_assignment
        .merge(target, on="SK_ID_CURR", validate="one_to_one")
        .groupby("SPLIT")
        .agg(
            clients=("SK_ID_CURR", "size"),
            default_rate=("TARGET", "mean"),
        )
    )

    split_summary["percentage"] = (
        split_summary["clients"]
        / split_summary["clients"].sum()
    )

    print("\nSplit summary:")
    print(split_summary)

    assert split_assignment["SK_ID_CURR"].is_unique
    assert split_assignment["SPLIT"].notna().all()

    print("\nSplit validation passed.")


def main() -> None:
    split_assignment = create_split_assignment(
        feature_store_path=FEATURE_STORE_PATH,
    )

    validate_split(
        split_assignment=split_assignment,
        feature_store_path=FEATURE_STORE_PATH,
    )

    split_assignment.to_parquet(
        SPLIT_PATH,
        index=False,
    )

    print(f"\nSplit assignment saved to: {SPLIT_PATH}")


if __name__ == "__main__":
    main()