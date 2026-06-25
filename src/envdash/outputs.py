from __future__ import annotations

from pathlib import Path

import pandas as pd

from .paths import PROCESSED_DIR, TABLES_DIR
from .validate import summarize_coverage


def write_integrated_outputs(integrated: pd.DataFrame, output_dir: Path = PROCESSED_DIR) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    integrated_path = output_dir / "integrated_environment_monthly.csv"
    coverage_path = TABLES_DIR / "data_coverage_summary.csv"
    integrated.to_csv(integrated_path, index=False)
    summarize_coverage(integrated).to_csv(coverage_path, index=False)
    return {"integrated": integrated_path, "coverage": coverage_path}


def write_model_outputs(
    features: pd.DataFrame,
    forecast: pd.DataFrame,
    forecast_evaluation: pd.DataFrame | None = None,
    source_validation: pd.DataFrame | None = None,
) -> dict[str, Path]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    features_path = PROCESSED_DIR / "monthly_features.csv"
    forecast_path = TABLES_DIR / "forecast_results.csv"
    forecast_evaluation_path = TABLES_DIR / "forecast_evaluation.csv"
    source_validation_path = TABLES_DIR / "source_validation_summary.csv"
    features.to_csv(features_path, index=False)
    forecast.to_csv(forecast_path, index=False)
    if forecast_evaluation is not None:
        forecast_evaluation.to_csv(forecast_evaluation_path, index=False)
    if source_validation is not None:
        source_validation.to_csv(source_validation_path, index=False)
    return {
        "features": features_path,
        "forecast": forecast_path,
        "forecast_evaluation": forecast_evaluation_path,
        "source_validation": source_validation_path,
    }
