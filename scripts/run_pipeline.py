#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from urllib.parse import urlencode

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import pandas as pd

from envdash.config import load_json_config
from envdash.features import build_monthly_features
from envdash.ingest import (
    aggregate_national_monthly,
    download_file,
    download_open_meteo_air_quality,
    download_open_meteo_weather,
    load_long_monthly_csv,
    load_nasa_power_monthly_csv,
    load_opendosm_air_pollution,
)
from envdash.models import backtest_forecast_models, forecast_with_models
from envdash.outputs import write_integrated_outputs, write_model_outputs
from envdash.paths import RAW_DIR, ensure_project_dirs
from envdash.validate import summarize_pm_source_validation


def _project_path(relative_path: str) -> Path:
    return PROJECT_ROOT / relative_path


def _nasa_power_region_url(config: dict, parameter: str, region: dict) -> str:
    window = config["analysis_window"]
    nasa = config["nasa_power"]
    end_year = min(int(window["end_year"]), int(nasa.get("available_end_year", window["end_year"])))
    query = {
        "latitude-min": region["latitude_min"],
        "latitude-max": region["latitude_max"],
        "longitude-min": region["longitude_min"],
        "longitude-max": region["longitude_max"],
        "parameters": parameter,
        "community": nasa["community"],
        "start": window["start_year"],
        "end": end_year,
        "format": nasa["format"],
    }
    return f"{nasa['base_url']}?{urlencode(query)}"


def _download_public_sources(config: dict) -> list[str]:
    messages: list[str] = []

    opendosm = config["opendosm_air_pollution"]
    opendosm_path = _project_path(opendosm["local_path"])
    if not opendosm_path.exists():
        try:
            download_file(opendosm["url"], opendosm_path)
            messages.append(f"Downloaded OpenDOSM baseline to {opendosm_path}")
        except Exception as exc:
            messages.append(f"Skipped OpenDOSM download: {exc}")

    nasa_dir = _project_path(config["nasa_power"]["local_dir"])
    nasa_dir.mkdir(parents=True, exist_ok=True)
    for parameter in config["nasa_power"]["parameters"]:
        for region in config["nasa_power"]["regions"]:
            output_path = nasa_dir / f"nasa_power_{parameter.lower()}_{region['name']}_monthly.csv"
            if output_path.exists():
                continue
            try:
                download_file(_nasa_power_region_url(config, parameter, region), output_path)
                messages.append(f"Downloaded NASA POWER {parameter} {region['name']} to {output_path}")
            except Exception as exc:
                messages.append(f"Skipped NASA POWER {parameter} {region['name']} download: {exc}")

    open_meteo = config.get("open_meteo_air_quality")
    if open_meteo:
        open_meteo_path = _project_path(open_meteo["local_path"])
        if not open_meteo_path.exists():
            try:
                download_open_meteo_air_quality(open_meteo, open_meteo_path)
                messages.append(f"Downloaded Open-Meteo CAMS modelled PM data to {open_meteo_path}")
            except Exception as exc:
                messages.append(f"Skipped Open-Meteo CAMS modelled PM download: {exc}")

    open_meteo_weather = config.get("open_meteo_weather")
    if open_meteo_weather:
        open_meteo_weather_path = _project_path(open_meteo_weather["local_path"])
        if not open_meteo_weather_path.exists():
            try:
                download_open_meteo_weather(open_meteo_weather, open_meteo_weather_path)
                messages.append(f"Downloaded Open-Meteo historical weather data to {open_meteo_weather_path}")
            except Exception as exc:
                messages.append(f"Skipped Open-Meteo historical weather download: {exc}")

    return messages


def _load_available_sources(config: dict) -> list[pd.DataFrame]:
    frames: list[pd.DataFrame] = []

    opendosm_path = _project_path(config["opendosm_air_pollution"]["local_path"])
    if opendosm_path.exists():
        frames.append(load_opendosm_air_pollution(opendosm_path))

    nasa_dir = _project_path(config["nasa_power"]["local_dir"])
    for csv_path in sorted(nasa_dir.glob("*.csv")):
        frames.append(load_nasa_power_monthly_csv(csv_path, source_name="NASA POWER monthly"))

    open_meteo = config.get("open_meteo_air_quality")
    if open_meteo:
        open_meteo_path = _project_path(open_meteo["local_path"])
        if open_meteo_path.exists():
            frames.append(load_long_monthly_csv(open_meteo_path, source_name=open_meteo["source_label"]))

    open_meteo_weather = config.get("open_meteo_weather")
    if open_meteo_weather:
        open_meteo_weather_path = _project_path(open_meteo_weather["local_path"])
        if open_meteo_weather_path.exists():
            frames.append(load_long_monthly_csv(open_meteo_weather_path, source_name=open_meteo_weather["source_label"]))

    return frames


def _target_history(integrated: pd.DataFrame, variable: str) -> pd.DataFrame:
    preferred_source = "Open-Meteo CAMS global modelled PM"
    preferred = integrated[
        (integrated["variable"] == variable)
        & (integrated["source"] == preferred_source)
    ][["date", "value"]]
    if not preferred.empty:
        return preferred
    return integrated[integrated["variable"] == variable][["date", "value"]]


def _make_forecasts(integrated: pd.DataFrame, model_config: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    features = build_monthly_features(integrated)
    forecasts: list[pd.DataFrame] = []
    evaluations: list[pd.DataFrame] = []
    horizon = int(model_config["forecast_horizon_months"])
    minimum_target_year = int(model_config.get("minimum_target_year", 2023))
    model_names = model_config.get(
        "forecast_models",
        ["naive", "seasonal_naive", "arima", "prophet_additive", "random_forest"],
    )
    validation_months = int(model_config.get("validation_months", min(6, horizon)))

    for variable in model_config["target_variables"]:
        history = _target_history(integrated, variable)
        if len(history) < 2 or history["date"].dt.year.max() < minimum_target_year:
            continue
        forecasts.append(forecast_with_models(history, horizon=horizon, model_names=model_names).assign(variable=variable))
        evaluations.append(
            backtest_forecast_models(history, validation_months=validation_months, model_names=model_names).assign(
                variable=variable
            )
        )

    forecast_frame = (
        pd.concat(forecasts, ignore_index=True)
        if forecasts
        else pd.DataFrame(columns=["date", "forecast", "model", "variable"])
    )
    evaluation_frame = (
        pd.concat(evaluations, ignore_index=True)
        if evaluations
        else pd.DataFrame(columns=["model", "validation_period", "n", "mae", "rmse", "variable"])
    )
    return features, forecast_frame, evaluation_frame


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local Malaysia environment dashboard pipeline.")
    parser.add_argument(
        "--download-public",
        action="store_true",
        help="Download public OpenDOSM and NASA POWER CSV files before processing.",
    )
    args = parser.parse_args()

    ensure_project_dirs()
    source_config = load_json_config("data_sources.json")
    model_config = load_json_config("model_config.json")

    if args.download_public:
        for message in _download_public_sources(source_config):
            print(message)

    frames = _load_available_sources(source_config)
    if not frames:
        print("No local source files found. Run with --download-public and check the configured local source paths.")
        return 0

    integrated = aggregate_national_monthly(pd.concat(frames, ignore_index=True)).sort_values(["source", "variable", "date"])
    output_paths = write_integrated_outputs(integrated)
    print(f"Wrote integrated dataset: {output_paths['integrated']}")
    print(f"Wrote coverage summary: {output_paths['coverage']}")

    features, forecast, forecast_evaluation = _make_forecasts(integrated, model_config)
    source_validation = summarize_pm_source_validation(integrated)
    model_paths = write_model_outputs(features, forecast, forecast_evaluation, source_validation)
    print(f"Wrote monthly features: {model_paths['features']}")
    if not forecast.empty:
        print(f"Wrote forecast table: {model_paths['forecast']}")
        print(f"Wrote forecast evaluation table: {model_paths['forecast_evaluation']}")
    else:
        print("No PM2.5/PM10 forecast produced yet; add CAMS manual pollutant data for 2023-2026.")
    print(f"Wrote PM source validation summary: {model_paths['source_validation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
