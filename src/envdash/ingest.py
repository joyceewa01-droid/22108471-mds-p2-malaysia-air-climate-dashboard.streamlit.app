from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from .validate import validate_long_frame


POLLUTANT_UNITS = {
    "PM2.5": "ug/m3",
    "PM10": "ug/m3",
    "NO2": "ppm",
    "SO2": "ppm",
    "O3": "ppm",
    "CO": "ppm",
}

OPEN_METEO_WEATHER_VARIABLES = {
    "temperature_2m_mean": ("T2M", "deg C", "mean"),
    "relative_humidity_2m_mean": ("RH2M", "%", "mean"),
    "wind_speed_10m_mean": ("WS2M", "m/s", "mean"),
    "precipitation_sum": ("PRECTOTCORR", "mm/month", "sum"),
}

MONTH_COLUMNS = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}


def download_file(url: str, destination: Path, timeout: int = 30) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "envdash-local-pipeline/1.0"})
    with urlopen(request, timeout=timeout) as response:
        destination.write_bytes(response.read())
    return destination


def download_open_meteo_air_quality(config: dict, destination: Path, timeout: int = 60) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    locations = config["locations"]
    query = {
        "latitude": ",".join(str(location["latitude"]) for location in locations),
        "longitude": ",".join(str(location["longitude"]) for location in locations),
        "hourly": "pm2_5,pm10",
        "start_date": config["start_date"],
        "end_date": config["end_date"],
        "timezone": config.get("timezone", "UTC"),
        "domains": config.get("domains", "cams_global"),
    }
    request = Request(
        f"{config['base_url']}?{urlencode(query)}",
        headers={"User-Agent": "envdash-local-pipeline/1.0"},
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    payloads = payload if isinstance(payload, list) else [payload]
    rows: list[pd.DataFrame] = []
    for index, item in enumerate(payloads):
        location = locations[index]
        hourly = item.get("hourly", {})
        if not hourly or "time" not in hourly:
            continue
        wide = pd.DataFrame(
            {
                "date": pd.to_datetime(hourly["time"]),
                "PM2.5": pd.to_numeric(hourly.get("pm2_5"), errors="coerce"),
                "PM10": pd.to_numeric(hourly.get("pm10"), errors="coerce"),
            }
        )
        long_frame = wide.melt(id_vars=["date"], var_name="variable", value_name="value")
        long_frame["location"] = location["name"]
        long_frame["source"] = config.get("source_label", "Open-Meteo CAMS global modelled PM")
        long_frame["unit"] = "ug/m3"
        rows.append(long_frame)

    if not rows:
        raise ValueError("Open-Meteo Air Quality API returned no usable PM2.5/PM10 rows")

    monthly = pd.concat(rows, ignore_index=True)
    monthly["date"] = monthly["date"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        monthly.groupby(["date", "variable", "source", "unit"], dropna=False)["value"]
        .mean()
        .reset_index()
        .sort_values(["variable", "date"])
    )
    monthly.to_csv(destination, index=False)
    return destination


def download_open_meteo_weather(config: dict, destination: Path, timeout: int = 60) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    locations = config["locations"]
    query = {
        "latitude": ",".join(str(location["latitude"]) for location in locations),
        "longitude": ",".join(str(location["longitude"]) for location in locations),
        "daily": config.get("daily", ",".join(OPEN_METEO_WEATHER_VARIABLES)),
        "start_date": config["start_date"],
        "end_date": config["end_date"],
        "timezone": config.get("timezone", "UTC"),
        "wind_speed_unit": config.get("wind_speed_unit", "ms"),
        "precipitation_unit": config.get("precipitation_unit", "mm"),
    }
    request = Request(
        f"{config['base_url']}?{urlencode(query)}",
        headers={"User-Agent": "envdash-local-pipeline/1.0"},
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    payloads = payload if isinstance(payload, list) else [payload]
    rows: list[pd.DataFrame] = []
    for index, item in enumerate(payloads):
        location = locations[index]
        daily = item.get("daily", {})
        if not daily or "time" not in daily:
            continue
        wide = pd.DataFrame({"date": pd.to_datetime(daily["time"])})
        for api_name in OPEN_METEO_WEATHER_VARIABLES:
            wide[api_name] = pd.to_numeric(daily.get(api_name), errors="coerce")
        long_frame = wide.melt(id_vars=["date"], var_name="api_variable", value_name="value")
        long_frame["variable"] = long_frame["api_variable"].map(
            {api_name: meta[0] for api_name, meta in OPEN_METEO_WEATHER_VARIABLES.items()}
        )
        long_frame["aggregation"] = long_frame["api_variable"].map(
            {api_name: meta[2] for api_name, meta in OPEN_METEO_WEATHER_VARIABLES.items()}
        )
        long_frame["location"] = location["name"]
        long_frame["source"] = config.get("source_label", "Open-Meteo historical weather")
        long_frame["unit"] = long_frame["api_variable"].map(
            {api_name: meta[1] for api_name, meta in OPEN_METEO_WEATHER_VARIABLES.items()}
        )
        rows.append(long_frame)

    if not rows:
        raise ValueError("Open-Meteo Historical Weather API returned no usable climate rows")

    daily_frame = pd.concat(rows, ignore_index=True)
    daily_frame["date"] = daily_frame["date"].dt.to_period("M").dt.to_timestamp()

    monthly_parts: list[pd.DataFrame] = []
    for aggregation, group in daily_frame.groupby("aggregation"):
        grouped = group.groupby(["date", "variable", "source", "unit", "location"], dropna=False)["value"]
        if aggregation == "sum":
            monthly_parts.append(grouped.sum(min_count=1).reset_index())
        else:
            monthly_parts.append(grouped.mean().reset_index())

    monthly_by_location = pd.concat(monthly_parts, ignore_index=True)
    monthly = (
        monthly_by_location.groupby(["date", "variable", "source", "unit"], dropna=False)["value"]
        .mean()
        .reset_index()
        .sort_values(["variable", "date"])
    )
    monthly.to_csv(destination, index=False)
    return destination


def _first_existing(columns: set[str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def _normalise_variable(value: object) -> str:
    text = str(value).strip().upper()
    text = text.replace("PM₂.₅", "PM2.5").replace("PM2_5", "PM2.5").replace("PM25", "PM2.5")
    text = text.replace("PM 2.5", "PM2.5").replace("PM 10", "PM10")
    return text


def _month_number(value: object) -> int:
    text = str(value).strip().upper()
    if text in MONTH_COLUMNS:
        return MONTH_COLUMNS[text]
    return int(text)


def load_opendosm_air_pollution(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    raw.columns = [str(column).strip().lower() for column in raw.columns]
    columns = set(raw.columns)

    date_col = _first_existing(columns, ["date", "month", "period"])
    variable_col = _first_existing(columns, ["pollutant", "variable", "indicator", "parameter"])
    value_col = _first_existing(columns, ["value", "concentration", "reading", "avg_value", "mean"])

    if date_col is None and {"year", "month"}.issubset(columns):
        raw["date"] = pd.to_datetime(dict(year=raw["year"], month=raw["month"], day=1))
        date_col = "date"
    if date_col is None or variable_col is None or value_col is None:
        raise ValueError(
            "OpenDOSM air pollution file must include date/month, pollutant/variable, and value/concentration columns"
        )

    frame = raw.rename(columns={date_col: "date", variable_col: "variable", value_col: "value"})
    frame["date"] = pd.to_datetime(frame["date"]).dt.to_period("M").dt.to_timestamp()
    frame["variable"] = frame["variable"].map(_normalise_variable)
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame["source"] = "OpenDOSM/DOE official baseline"
    frame["unit"] = frame["variable"].map(POLLUTANT_UNITS).fillna("reported")
    long_frame = frame[["date", "variable", "value", "source", "unit"]]
    return aggregate_national_monthly(long_frame)


def load_nasa_power_monthly_csv(path: Path, source_name: str = "NASA POWER monthly") -> pd.DataFrame:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    header_index = next((index for index, line in enumerate(lines) if line.upper().startswith("PARAMETER,YEAR")), None)
    if header_index is None:
        header_index = next(
            (
                index
                for index, line in enumerate(lines)
                if "YEAR" in line.upper() and ("MO" in line.upper() or "MONTH" in line.upper())
            ),
            0,
        )
    raw = pd.read_csv(StringIO("\n".join(lines[header_index:])))
    raw.columns = [str(column).strip().upper() for column in raw.columns]

    if {"YEAR", "MO"}.issubset(raw.columns):
        raw["date"] = pd.to_datetime(dict(year=raw["YEAR"], month=raw["MO"], day=1))
        id_columns = [column for column in ["LAT", "LON", "YEAR", "MO", "date"] if column in raw.columns]
        value_columns = [column for column in raw.columns if column not in id_columns]
        long_frame = raw.melt(id_vars=["date"], value_vars=value_columns, var_name="variable", value_name="value")
    elif {"YEAR", "PARAMETER"}.issubset(raw.columns):
        month_columns = [column for column in raw.columns if column.isdigit() or column in MONTH_COLUMNS]
        melted = raw.melt(id_vars=["YEAR", "PARAMETER"], value_vars=month_columns, var_name="month", value_name="value")
        melted["month"] = melted["month"].map(_month_number)
        melted["date"] = pd.to_datetime(dict(year=melted["YEAR"], month=melted["month"].astype(int), day=1))
        long_frame = melted.rename(columns={"PARAMETER": "variable"})[["date", "variable", "value"]]
    else:
        raise ValueError("NASA POWER monthly CSV must contain YEAR/MO columns or YEAR/PARAMETER monthly columns")

    long_frame["variable"] = long_frame["variable"].astype(str).str.upper()
    long_frame["value"] = pd.to_numeric(long_frame["value"], errors="coerce")
    long_frame.loc[long_frame["value"] == -999, "value"] = pd.NA
    long_frame["source"] = source_name
    long_frame["unit"] = "reported"
    return aggregate_national_monthly(long_frame[["date", "variable", "value", "source", "unit"]])


def load_long_monthly_csv(path: Path, source_name: str = "Monthly data") -> pd.DataFrame:
    raw = pd.read_csv(path)
    raw.columns = [str(column).strip().lower() for column in raw.columns]
    required = {"date", "variable", "value"}
    missing = sorted(required.difference(raw.columns))
    if missing:
        raise ValueError(f"Monthly CSV is missing required columns: {', '.join(missing)}")

    frame = raw.rename(columns={"date": "date", "variable": "variable", "value": "value"})
    frame["date"] = pd.to_datetime(frame["date"]).dt.to_period("M").dt.to_timestamp()
    frame["variable"] = frame["variable"].map(_normalise_variable)
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame["source"] = raw["source"] if "source" in raw.columns else source_name
    frame["unit"] = raw["unit"] if "unit" in raw.columns else frame["variable"].map(POLLUTANT_UNITS).fillna("reported")
    return aggregate_national_monthly(frame[["date", "variable", "value", "source", "unit"]])


def aggregate_national_monthly(frame: pd.DataFrame) -> pd.DataFrame:
    valid = validate_long_frame(frame)
    national = (
        valid.groupby(["date", "variable", "source", "unit"], dropna=False)["value"]
        .mean()
        .reset_index()
        .sort_values(["source", "variable", "date"])
        .reset_index(drop=True)
    )
    return national
