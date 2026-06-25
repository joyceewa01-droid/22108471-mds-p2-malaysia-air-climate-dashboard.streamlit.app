from __future__ import annotations

import pandas as pd


REQUIRED_LONG_COLUMNS = {"date", "variable", "value", "source", "unit"}


def validate_long_frame(frame: pd.DataFrame, required: set[str] | None = None) -> pd.DataFrame:
    required_columns = REQUIRED_LONG_COLUMNS if required is None else required
    missing = sorted(required_columns.difference(frame.columns))
    if missing:
        raise ValueError(f"Input frame is missing required columns: {', '.join(missing)}")

    result = frame.copy()
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result["value"] = pd.to_numeric(result["value"], errors="coerce")
    if result["date"].isna().any():
        raise ValueError("Input frame contains invalid date values")
    return result


def summarize_coverage(frame: pd.DataFrame) -> pd.DataFrame:
    valid = validate_long_frame(frame)
    grouped = (
        valid.groupby(["source", "variable"], dropna=False)
        .agg(
            start_date=("date", "min"),
            end_date=("date", "max"),
            rows=("value", "size"),
            missing_values=("value", lambda values: int(values.isna().sum())),
        )
        .reset_index()
    )
    return grouped


def summarize_pm_source_validation(
    frame: pd.DataFrame,
    official_source: str = "OpenDOSM/DOE official baseline",
    modelled_source: str = "Open-Meteo CAMS global modelled PM",
) -> pd.DataFrame:
    valid = validate_long_frame(frame)
    rows: list[dict[str, object]] = []
    variables = sorted({"PM2.5", "PM10"}.intersection(set(valid["variable"].dropna().unique())))
    for variable in variables:
        view = valid[
            (valid["variable"] == variable)
            & (valid["source"].isin([official_source, modelled_source]))
        ][["date", "source", "value"]].copy()
        if view.empty:
            rows.append(
                {
                    "variable": variable,
                    "official_source": official_source,
                    "modelled_source": modelled_source,
                    "overlap_months": 0,
                    "overlap_period": "No overlap",
                    "official_mean": pd.NA,
                    "modelled_mean": pd.NA,
                    "mean_bias_modelled_minus_official": pd.NA,
                    "mae": pd.NA,
                    "rmse": pd.NA,
                    "correlation": pd.NA,
                    "status": "No overlap in local data",
                }
            )
            continue

        pivot = (
            view.pivot_table(index="date", columns="source", values="value", aggfunc="mean")
            .dropna(subset=[official_source, modelled_source], how="any")
            .reset_index()
        )
        if pivot.empty:
            rows.append(
                {
                    "variable": variable,
                    "official_source": official_source,
                    "modelled_source": modelled_source,
                    "overlap_months": 0,
                    "overlap_period": "No overlap",
                    "official_mean": pd.NA,
                    "modelled_mean": pd.NA,
                    "mean_bias_modelled_minus_official": pd.NA,
                    "mae": pd.NA,
                    "rmse": pd.NA,
                    "correlation": pd.NA,
                    "status": "No overlap in local data",
                }
            )
            continue

        errors = pivot[modelled_source].astype(float) - pivot[official_source].astype(float)
        correlation = (
            float(pivot[[official_source, modelled_source]].corr().iloc[0, 1])
            if len(pivot) > 1
            else pd.NA
        )
        rows.append(
            {
                "variable": variable,
                "official_source": official_source,
                "modelled_source": modelled_source,
                "overlap_months": int(len(pivot)),
                "overlap_period": (
                    f"{pivot['date'].min().strftime('%Y-%m')} to "
                    f"{pivot['date'].max().strftime('%Y-%m')}"
                ),
                "official_mean": float(pivot[official_source].mean()),
                "modelled_mean": float(pivot[modelled_source].mean()),
                "mean_bias_modelled_minus_official": float(errors.mean()),
                "mae": float(errors.abs().mean()),
                "rmse": float((errors.pow(2).mean()) ** 0.5),
                "correlation": correlation,
                "status": "Overlap available",
            }
        )
    return pd.DataFrame(rows)
