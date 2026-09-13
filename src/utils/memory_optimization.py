import numpy as np
import pandas as pd
from pandas.api.types import is_float_dtype, is_integer_dtype, is_numeric_dtype


def reduce_memory_usage(df: pd.DataFrame) -> pd.DataFrame:
    """Downcast numeric columns to reduce DataFrame memory usage.

    Integer columns are converted to the smallest NumPy integer dtype that can
    represent the observed range. Floating-point columns are converted to
    float32 whenever their observed range fits in float32; otherwise float64 is
    preserved/used.

    float16 is intentionally avoided. Although it can reduce memory further,
    its limited range and precision are generally unsuitable for a feature
    store and can also trigger overflow warnings during pandas formatting and
    downstream numerical operations.

    Non-numeric columns, booleans, datetimes, categoricals, and extension dtypes
    that are not standard NumPy integers/floats are left unchanged.

    Args:
        df: Input DataFrame to optimize in place.

    Returns:
        The same DataFrame with optimized numeric dtypes.
    """
    start_mem = df.memory_usage(deep=True).sum() / 1024**2
    print(f"Memory usage of dataframe is {start_mem:.2f} MB")

    for col in df.columns:
        series = df[col]
        col_type = series.dtype

        # Skip non-numeric columns and booleans.
        if not is_numeric_dtype(col_type) or pd.api.types.is_bool_dtype(col_type):
            continue

        # Avoid converting nullable/extension dtypes with astype(np.int*)
        # unless they are plain NumPy integer/float dtypes.
        if is_integer_dtype(col_type):
            c_min = series.min()
            c_max = series.max()

            if pd.isna(c_min) or pd.isna(c_max):
                continue

            if c_min >= np.iinfo(np.int8).min and c_max <= np.iinfo(np.int8).max:
                df[col] = series.astype(np.int8)
            elif c_min >= np.iinfo(np.int16).min and c_max <= np.iinfo(np.int16).max:
                df[col] = series.astype(np.int16)
            elif c_min >= np.iinfo(np.int32).min and c_max <= np.iinfo(np.int32).max:
                df[col] = series.astype(np.int32)
            else:
                df[col] = series.astype(np.int64)

        elif is_float_dtype(col_type):
            c_min = series.min()
            c_max = series.max()

            # All-NaN float columns can safely be stored as float32.
            if pd.isna(c_min) and pd.isna(c_max):
                df[col] = series.astype(np.float32)
                continue

            float32_info = np.finfo(np.float32)
            if c_min >= float32_info.min and c_max <= float32_info.max:
                df[col] = series.astype(np.float32)
            else:
                df[col] = series.astype(np.float64)

    end_mem = df.memory_usage(deep=True).sum() / 1024**2
    print(f"Memory usage after optimization is: {end_mem:.2f} MB")

    reduction = 0.0 if start_mem == 0 else 100 * (start_mem - end_mem) / start_mem
    print(f"Decreased by {reduction:.1f}%")

    return df