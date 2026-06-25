from __future__ import annotations

import pandas as pd

from .validate import validate_long_frame


def build_monthly_features(
    frame: pd.DataFrame,
    value_col: str = "value",
    group_cols: tuple[str, ...] = ("source", "variable"),
) -> pd.DataFrame:
    result = validate_long_frame(frame).copy()
    result = result.sort_values([*group_cols, "date"]).reset_index(drop=True)
    result["year"] = result["date"].dt.year
    result["month"] = result["date"].dt.month

    grouped = result.groupby(list(group_cols), dropna=False)[value_col]
    for lag in (1, 2, 3, 12):
        result[f"{value_col}_lag_{lag}"] = grouped.shift(lag)
    result[f"{value_col}_roll_3"] = grouped.transform(lambda values: values.rolling(3, min_periods=1).mean())
    result[f"{value_col}_roll_6"] = grouped.transform(lambda values: values.rolling(6, min_periods=1).mean())
    result[f"{value_col}_yoy_delta"] = result[value_col] - result[f"{value_col}_lag_12"]
    return result
