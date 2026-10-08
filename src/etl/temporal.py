"""Conservative availability checks relative to the current application."""

import warnings
import pandas as pd


def historical_rows(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Keep rows with all observation dates strictly before application.

    Zero is excluded because day/month resolution cannot establish availability
    before scoring. Missing or invalid dates are excluded, never imputed.
    Scheduled future dates should not be passed as observation dates.
    """
    missing = set(columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing temporal columns: {sorted(missing)}")
    dates = df[columns].apply(pd.to_numeric, errors="coerce")
    valid = (dates.lt(0) & dates.gt(float("-inf"))).all(axis=1)
    excluded = int((~valid).sum())
    if excluded:
        warnings.warn(
            f"Temporal cutoff excluded {excluded} rows: {columns} must be "
            "numeric, finite, non-null and strictly negative.",
            UserWarning,
            stacklevel=2,
        )
    out = df.loc[valid].copy()
    for column in columns:
        out[column] = dates.loc[valid, column]
    return out
