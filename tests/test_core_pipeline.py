import unittest
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from envdash.features import build_monthly_features
from envdash.models import (
    arima_forecast,
    backtest_forecast_models,
    naive_forecast,
    prophet_style_forecast,
    random_forest_forecast,
    seasonal_naive_forecast,
)
from envdash.validate import summarize_pm_source_validation, validate_long_frame


class CorePipelineTests(unittest.TestCase):
    def test_validate_required_columns_accepts_source_label(self):
        frame = pd.DataFrame(
            {
                "date": ["2024-01-01"],
                "variable": ["PM2.5"],
                "value": [12.4],
                "source": ["sample"],
                "unit": ["ug/m3"],
            }
        )

        result = validate_long_frame(frame)

        self.assertEqual(list(result.columns), list(frame.columns))

    def test_validate_required_columns_rejects_missing_source(self):
        frame = pd.DataFrame(
            {
                "date": ["2024-01-01"],
                "variable": ["PM2.5"],
                "value": [12.4],
                "unit": ["ug/m3"],
            }
        )

        with self.assertRaisesRegex(ValueError, "source"):
            validate_long_frame(frame)

    def test_build_monthly_features_adds_lag_and_rolling(self):
        frame = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=4, freq="MS"),
                "variable": ["PM2.5"] * 4,
                "value": [10.0, 12.0, 14.0, 16.0],
                "source": ["sample"] * 4,
                "unit": ["ug/m3"] * 4,
            }
        )

        features = build_monthly_features(frame)

        self.assertIn("value_lag_1", features.columns)
        self.assertIn("value_roll_3", features.columns)
        self.assertEqual(features.loc[1, "value_lag_1"], 10.0)
        self.assertEqual(features.loc[2, "value_roll_3"], 12.0)

    def test_naive_forecast_uses_last_observation(self):
        history = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=3, freq="MS"),
                "value": [10.0, 12.0, 14.0],
            }
        )

        forecast = naive_forecast(history, horizon=2)

        self.assertEqual(forecast["forecast"].tolist(), [14.0, 14.0])
        self.assertEqual(forecast["date"].dt.strftime("%Y-%m-%d").tolist(), ["2024-04-01", "2024-05-01"])

    def test_seasonal_naive_uses_previous_season_when_available(self):
        history = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=14, freq="MS"),
                "value": [float(i) for i in range(14)],
            }
        )

        forecast = seasonal_naive_forecast(history, horizon=2, season_length=12)

        self.assertEqual(forecast["forecast"].tolist(), [2.0, 3.0])

    def test_advanced_forecasts_return_horizon_and_model_labels(self):
        history = pd.DataFrame(
            {
                "date": pd.date_range("2022-01-01", periods=30, freq="MS"),
                "value": [12.0 + (i * 0.2) + ((i % 12) * 0.1) for i in range(30)],
            }
        )

        arima = arima_forecast(history, horizon=3)
        prophet = prophet_style_forecast(history, horizon=3)
        random_forest = random_forest_forecast(history, horizon=3)

        self.assertEqual(arima["model"].unique().tolist(), ["arima"])
        self.assertEqual(prophet["model"].unique().tolist(), ["prophet_additive"])
        self.assertEqual(random_forest["model"].unique().tolist(), ["random_forest"])
        self.assertEqual(len(arima), 3)
        self.assertEqual(len(prophet), 3)
        self.assertEqual(len(random_forest), 3)
        self.assertFalse(arima["forecast"].isna().any())
        self.assertFalse(prophet["forecast"].isna().any())
        self.assertFalse(random_forest["forecast"].isna().any())

    def test_backtest_forecast_models_reports_error_metrics(self):
        history = pd.DataFrame(
            {
                "date": pd.date_range("2022-01-01", periods=30, freq="MS"),
                "value": [15.0 + (i % 12) * 0.3 for i in range(30)],
            }
        )

        evaluation = backtest_forecast_models(history, validation_months=6)

        self.assertIn("model", evaluation.columns)
        self.assertIn("mae", evaluation.columns)
        self.assertIn("rmse", evaluation.columns)
        self.assertTrue({"naive", "seasonal_naive", "arima", "prophet_additive", "random_forest"}.issubset(set(evaluation["model"])))
        self.assertTrue((evaluation["n"] == 6).all())

    def test_pm_source_validation_reports_overlap_metrics_when_available(self):
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(["2022-11-01", "2022-12-01", "2022-11-01", "2022-12-01"]),
                "variable": ["PM2.5", "PM2.5", "PM2.5", "PM2.5"],
                "value": [10.0, 14.0, 11.0, 13.0],
                "source": [
                    "OpenDOSM/DOE official baseline",
                    "OpenDOSM/DOE official baseline",
                    "Open-Meteo CAMS global modelled PM",
                    "Open-Meteo CAMS global modelled PM",
                ],
                "unit": ["ug/m3"] * 4,
            }
        )

        validation = summarize_pm_source_validation(frame)

        self.assertEqual(len(validation), 1)
        self.assertEqual(validation.loc[0, "variable"], "PM2.5")
        self.assertEqual(validation.loc[0, "overlap_months"], 2)
        self.assertAlmostEqual(validation.loc[0, "mean_bias_modelled_minus_official"], 0.0)
        self.assertEqual(validation.loc[0, "status"], "Overlap available")

    def test_pm_source_validation_reports_no_overlap(self):
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(["2022-12-01", "2023-01-01"]),
                "variable": ["PM10", "PM10"],
                "value": [20.0, 21.0],
                "source": ["OpenDOSM/DOE official baseline", "Open-Meteo CAMS global modelled PM"],
                "unit": ["ug/m3", "ug/m3"],
            }
        )

        validation = summarize_pm_source_validation(frame)

        self.assertEqual(validation.loc[0, "overlap_months"], 0)
        self.assertEqual(validation.loc[0, "status"], "No overlap in local data")


if __name__ == "__main__":
    unittest.main()
