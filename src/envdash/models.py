from __future__ import annotations

import math
import warnings

import numpy as np
import pandas as pd


def _next_months(last_date: pd.Timestamp, horizon: int) -> pd.DatetimeIndex:
    if horizon < 1:
        raise ValueError("horizon must be at least 1")
    start = (pd.Timestamp(last_date).to_period("M") + 1).to_timestamp()
    return pd.date_range(start, periods=horizon, freq="MS")


def _prepare_history(history: pd.DataFrame, date_col: str = "date", value_col: str = "value") -> pd.DataFrame:
    if history.empty:
        raise ValueError("history must not be empty")
    ordered = history[[date_col, value_col]].copy()
    ordered[date_col] = pd.to_datetime(ordered[date_col])
    ordered[value_col] = pd.to_numeric(ordered[value_col], errors="coerce")
    ordered = ordered.dropna(subset=[date_col, value_col]).sort_values(date_col).reset_index(drop=True)
    if ordered.empty:
        raise ValueError("history must contain at least one valid value")
    return ordered


def naive_forecast(
    history: pd.DataFrame,
    horizon: int,
    date_col: str = "date",
    value_col: str = "value",
) -> pd.DataFrame:
    if history.empty:
        raise ValueError("history must not be empty")
    ordered = _prepare_history(history, date_col, value_col)
    last_value = float(ordered[value_col].dropna().iloc[-1])
    dates = _next_months(ordered[date_col].max(), horizon)
    return pd.DataFrame({"date": dates, "forecast": [last_value] * horizon, "model": "naive"})


def seasonal_naive_forecast(
    history: pd.DataFrame,
    horizon: int,
    season_length: int = 12,
    date_col: str = "date",
    value_col: str = "value",
) -> pd.DataFrame:
    ordered = _prepare_history(history, date_col, value_col)
    values = ordered[value_col].astype(float).tolist()
    last_value = values[-1]
    forecasts: list[float] = []
    for step in range(1, horizon + 1):
        index = len(values) - season_length + step - 1
        forecasts.append(values[index] if 0 <= index < len(values) else last_value)
    dates = _next_months(ordered[date_col].max(), horizon)
    return pd.DataFrame({"date": dates, "forecast": forecasts, "model": "seasonal_naive"})


def arima_forecast(
    history: pd.DataFrame,
    horizon: int,
    date_col: str = "date",
    value_col: str = "value",
) -> pd.DataFrame:
    ordered = _prepare_history(history, date_col, value_col)
    dates = _next_months(ordered[date_col].max(), horizon)
    if len(ordered) < 6:
        fallback = naive_forecast(ordered, horizon, date_col, value_col)
        fallback["model"] = "arima"
        return fallback

    try:
        from statsmodels.tsa.arima.model import ARIMA

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fitted = ARIMA(ordered[value_col].astype(float), order=(1, 1, 1)).fit()
            values = fitted.forecast(steps=horizon)
        forecasts = [float(value) for value in values]
    except Exception:
        fallback = naive_forecast(ordered, horizon, date_col, value_col)
        forecasts = fallback["forecast"].astype(float).tolist()
    return pd.DataFrame({"date": dates, "forecast": forecasts, "model": "arima"})


def prophet_style_forecast(
    history: pd.DataFrame,
    horizon: int,
    date_col: str = "date",
    value_col: str = "value",
) -> pd.DataFrame:
    ordered = _prepare_history(history, date_col, value_col)
    dates = _next_months(ordered[date_col].max(), horizon)
    t = np.arange(len(ordered), dtype=float)
    month_angle = 2 * np.pi * (ordered[date_col].dt.month.to_numpy(dtype=float) - 1) / 12
    x_train = np.column_stack(
        [
            np.ones(len(ordered)),
            t,
            np.sin(month_angle),
            np.cos(month_angle),
        ]
    )
    y_train = ordered[value_col].to_numpy(dtype=float)
    coefficients, *_ = np.linalg.lstsq(x_train, y_train, rcond=None)

    future_t = np.arange(len(ordered), len(ordered) + horizon, dtype=float)
    future_angle = 2 * np.pi * (dates.month.to_numpy(dtype=float) - 1) / 12
    x_future = np.column_stack(
        [
            np.ones(horizon),
            future_t,
            np.sin(future_angle),
            np.cos(future_angle),
        ]
    )
    forecasts = x_future @ coefficients
    return pd.DataFrame(
        {
            "date": dates,
            "forecast": [float(value) for value in forecasts],
            "model": "prophet_additive",
        }
    )


def _supervised_rows(values: list[float], dates: pd.Series, start_index: int = 1) -> tuple[pd.DataFrame, pd.Series]:
    rows: list[dict[str, float]] = []
    targets: list[float] = []
    for index in range(start_index, len(values)):
        current_date = pd.Timestamp(dates.iloc[index])
        lag_1 = values[index - 1]
        lag_2 = values[index - 2] if index >= 2 else lag_1
        lag_12 = values[index - 12] if index >= 12 else lag_1
        month_angle = 2 * np.pi * (current_date.month - 1) / 12
        rows.append(
            {
                "t": float(index),
                "month_sin": float(np.sin(month_angle)),
                "month_cos": float(np.cos(month_angle)),
                "lag_1": lag_1,
                "lag_2": lag_2,
                "lag_12": lag_12,
            }
        )
        targets.append(values[index])
    return pd.DataFrame(rows), pd.Series(targets, dtype=float)


def random_forest_forecast(
    history: pd.DataFrame,
    horizon: int,
    date_col: str = "date",
    value_col: str = "value",
) -> pd.DataFrame:
    ordered = _prepare_history(history, date_col, value_col)
    dates = _next_months(ordered[date_col].max(), horizon)
    values = ordered[value_col].astype(float).tolist()
    if len(values) < 8:
        fallback = naive_forecast(ordered, horizon, date_col, value_col)
        fallback["model"] = "random_forest"
        return fallback

    x_train, y_train = _supervised_rows(values, ordered[date_col])
    try:
        from sklearn.ensemble import RandomForestRegressor

        model = RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=42)
        model.fit(x_train, y_train)
    except Exception:
        fallback = seasonal_naive_forecast(ordered, horizon, date_col, value_col)
        fallback["model"] = "random_forest"
        return fallback

    extended_values = values[:]
    forecasts: list[float] = []
    for step, future_date in enumerate(dates, start=1):
        index = len(values) + step - 1
        lag_1 = extended_values[-1]
        lag_2 = extended_values[-2] if len(extended_values) >= 2 else lag_1
        lag_12 = extended_values[-12] if len(extended_values) >= 12 else lag_1
        month_angle = 2 * np.pi * (pd.Timestamp(future_date).month - 1) / 12
        features = pd.DataFrame(
            [
                {
                    "t": float(index),
                    "month_sin": float(np.sin(month_angle)),
                    "month_cos": float(np.cos(month_angle)),
                    "lag_1": lag_1,
                    "lag_2": lag_2,
                    "lag_12": lag_12,
                }
            ]
        )
        prediction = float(model.predict(features)[0])
        forecasts.append(prediction)
        extended_values.append(prediction)
    return pd.DataFrame({"date": dates, "forecast": forecasts, "model": "random_forest"})


def evaluate_forecast(actual: pd.DataFrame, forecast: pd.DataFrame) -> dict[str, float | int]:
    merged = actual.merge(forecast, on="date", how="inner")
    if merged.empty:
        return {"n": 0, "mae": math.nan, "rmse": math.nan}
    errors = merged["value"].astype(float) - merged["forecast"].astype(float)
    return {
        "n": int(len(merged)),
        "mae": float(errors.abs().mean()),
        "rmse": float((errors.pow(2).mean()) ** 0.5),
    }


FORECAST_MODEL_FUNCTIONS = {
    "naive": naive_forecast,
    "seasonal_naive": seasonal_naive_forecast,
    "arima": arima_forecast,
    "prophet_additive": prophet_style_forecast,
    "random_forest": random_forest_forecast,
}


def forecast_with_models(history: pd.DataFrame, horizon: int, model_names: list[str] | None = None) -> pd.DataFrame:
    selected = model_names or list(FORECAST_MODEL_FUNCTIONS)
    forecasts: list[pd.DataFrame] = []
    for model_name in selected:
        model_function = FORECAST_MODEL_FUNCTIONS[model_name]
        forecasts.append(model_function(history, horizon=horizon))
    return pd.concat(forecasts, ignore_index=True)


def backtest_forecast_models(
    history: pd.DataFrame,
    validation_months: int,
    model_names: list[str] | None = None,
) -> pd.DataFrame:
    ordered = _prepare_history(history)
    if validation_months < 1:
        raise ValueError("validation_months must be at least 1")
    if len(ordered) <= validation_months + 2:
        return pd.DataFrame(columns=["model", "validation_period", "n", "mae", "rmse"])

    train = ordered.iloc[:-validation_months].copy()
    actual = ordered.iloc[-validation_months:].copy()
    rows: list[dict[str, float | int | str]] = []
    for model_name in model_names or list(FORECAST_MODEL_FUNCTIONS):
        forecast = FORECAST_MODEL_FUNCTIONS[model_name](train, horizon=validation_months)
        metrics = evaluate_forecast(actual, forecast)
        rows.append(
            {
                "model": model_name,
                "validation_period": (
                    f"{actual['date'].min().strftime('%Y-%m')} to "
                    f"{actual['date'].max().strftime('%Y-%m')}"
                ),
                **metrics,
            }
        )
    return pd.DataFrame(rows)
