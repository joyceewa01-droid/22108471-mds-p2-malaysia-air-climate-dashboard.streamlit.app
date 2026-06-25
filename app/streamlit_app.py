from __future__ import annotations

from pathlib import Path
import sys

import altair as alt
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from envdash.paths import PROCESSED_DIR, TABLES_DIR


st.set_page_config(page_title="Malaysia Air Quality and Climate Dashboard", layout="wide")

RESEARCH_TITLE = "An Interactive Analytics Dashboard for Air Quality and Climate Trend Analysis and Forecasting in Malaysia"
ANALYSIS_START = pd.Timestamp("2023-01-01")
ANALYSIS_END = pd.Timestamp("2026-12-01")

ICONS = {
    "overview": "🌿",
    "climate": "🌦️",
    "air": "🟢",
    "forecast": "📈",
    "appendix": "📎",
    "data": "📊",
    "baseline": "🏛️",
    "coverage": "🗓️",
    "validation": "🧪",
    "reference": "🔗",
    "warning": "⚠️",
    "temperature": "🌡️",
    "rainfall": "🌧️",
    "wind": "💨",
    "particles": "🟤",
}

ICON_STYLES = {
    "overview": ("#0f7a5a", "#dff3ea"),
    "climate": ("#2f766d", "#e2f0ec"),
    "air": ("#5d7f32", "#edf5dd"),
    "forecast": ("#287a68", "#dcefeb"),
    "appendix": ("#35695f", "#e5f1ee"),
    "data": ("#0f7a5a", "#dff3ea"),
    "baseline": ("#4d7f37", "#e7f3df"),
    "coverage": ("#357f66", "#e0f2ec"),
    "validation": ("#6f7a2f", "#f1f3d9"),
    "reference": ("#416f62", "#e6f0ed"),
    "warning": ("#9a5b17", "#fff0d8"),
    "temperature": ("#9a5b17", "#fff0d8"),
    "rainfall": ("#287a68", "#dcefeb"),
    "wind": ("#357f66", "#e0f2ec"),
    "particles": ("#5d7f32", "#edf5dd"),
}

VARIABLE_LABELS = {
    "PM2.5": "Fine particles (PM2.5)",
    "PM10": "Coarse particles (PM10)",
    "CO": "Carbon monoxide",
    "NO2": "Nitrogen dioxide",
    "O3": "Ozone",
    "SO2": "Sulphur dioxide",
    "T2M": "Temperature",
    "RH2M": "Relative humidity",
    "WS2M": "Wind speed",
    "PRECTOTCORR": "Rainfall",
}

VARIABLE_UNITS = {
    "PM2.5": "micrograms per cubic metre",
    "PM10": "micrograms per cubic metre",
    "CO": "ppm",
    "NO2": "ppm",
    "O3": "ppm",
    "SO2": "ppm",
    "T2M": "deg C",
    "RH2M": "%",
    "WS2M": "m/s",
    "PRECTOTCORR": "mm/month",
}

COMPACT_UNITS = {
    "PM2.5": "ug/m3",
    "PM10": "ug/m3",
    "CO": "ppm",
    "NO2": "ppm",
    "O3": "ppm",
    "SO2": "ppm",
    "T2M": "deg C",
    "RH2M": "%",
    "WS2M": "m/s",
    "PRECTOTCORR": "mm/month",
}

AIR_POLLUTION_VARIABLES = {"PM2.5", "PM10", "CO", "NO2", "O3", "SO2"}
CLIMATE_VARIABLES = {"T2M", "RH2M", "WS2M", "PRECTOTCORR"}
VARIABLE_EXPLANATIONS = {
    "PM2.5": "PM means particulate matter. PM2.5 is very fine particle pollution, about 2.5 micrometres or smaller, that can travel deep into the lungs.",
    "PM10": "PM10 is larger particle pollution, about 10 micrometres or smaller, often linked with dust, haze and coarse airborne particles.",
    "CO": "Carbon monoxide is a gas produced by burning fuel. In this dashboard it appears only in older official comparison data.",
    "NO2": "Nitrogen dioxide is a traffic and combustion-related gas. In this dashboard it appears only in older official comparison data.",
    "O3": "Ozone near the ground is a pollutant formed through chemical reactions in sunlight. In this dashboard it appears only in older official comparison data.",
    "SO2": "Sulphur dioxide is a gas linked with fuel burning and industrial emissions. In this dashboard it appears only in older official comparison data.",
    "T2M": "Temperature shows how warm the month was. It helps explain background conditions that may affect comfort and pollution formation.",
    "RH2M": "Relative humidity shows how much moisture is in the air. It can affect haze, visibility and how particles behave.",
    "WS2M": "Wind speed shows how strongly air is moving. Stronger wind can disperse pollution; weak wind can allow pollution to stay around.",
    "PRECTOTCORR": "Rainfall shows how much rain fell during the month. Rain can help remove particles from the air.",
}

AQI_CATEGORIES = [
    ("Good", "0-50", "#8dbf8a", "Air quality is generally satisfactory."),
    ("Moderate", "51-100", "#d8cf72", "Usually acceptable, but sensitive people may still pay attention."),
    ("Sensitive groups", "101-150", "#d49a61", "People with breathing or heart concerns should be more careful."),
    ("Unhealthy", "151-200", "#c86f67", "More people may feel effects; reduce heavy outdoor activity."),
    ("Very unhealthy", "201-300", "#9a7bb6", "Health alert level; outdoor activity should be limited."),
    ("Hazardous", "301+", "#7c4a5b", "Emergency-level warning; follow official advice."),
]

RAINFALL_BANDS = [
    ("Low rainfall", 0.0, 100.0, "#d8c98b", "Generally drier month. Outdoor plans may face fewer rain interruptions, but dry air may not help clear particles as much."),
    ("Moderate rainfall", 100.0, 200.0, "#94b7a0", "Noticeable rain during the month. Rain can help wash some particles from the air."),
    ("Wet month", 200.0, 300.0, "#6f9eb1", "Rain is more frequent or heavier. This may affect travel and outdoor planning."),
    ("Very wet month", 300.0, 1000.0, "#4d738b", "Very rainy month. Users should pay closer attention to flood, travel and outdoor-activity advisories."),
]

PM_BREAKPOINTS = {
    "PM2.5": [
        ("Good", 0.0, 12.0, "#8dbf8a"),
        ("Moderate", 12.0, 35.5, "#d8cf72"),
        ("Sensitive groups", 35.5, 55.5, "#d49a61"),
        ("Unhealthy", 55.5, 150.5, "#c86f67"),
        ("Very unhealthy", 150.5, 250.5, "#9a7bb6"),
        ("Hazardous", 250.5, 500.5, "#7c4a5b"),
    ],
    "PM10": [
        ("Good", 0.0, 55.0, "#8dbf8a"),
        ("Moderate", 55.0, 155.0, "#d8cf72"),
        ("Sensitive groups", 155.0, 255.0, "#d49a61"),
        ("Unhealthy", 255.0, 355.0, "#c86f67"),
        ("Very unhealthy", 355.0, 425.0, "#9a7bb6"),
        ("Hazardous", 425.0, 605.0, "#7c4a5b"),
    ],
}

DESIGN_REFERENCES = [
    {
        "decision": "Top menu with clearly labelled sections",
        "rationale": (
            "GOV.UK Design System guidance treats tabs as useful for quickly switching between related content, "
            "but warns that hidden content can be missed. The dashboard therefore keeps the menu visible near the top "
            "and uses short page labels rather than a hidden technical sidebar menu."
        ),
        "source": "GOV.UK Design System - Tabs",
        "citation": "GOV.UK Design System, n.d.",
        "url": "https://design-system.service.gov.uk/components/tabs/",
    },
    {
        "decision": "Simple time-series charts with nearby explanation",
        "rationale": (
            "The UK Government Analysis Function recommends choosing charts based on the message, keeping charts simple, "
            "using clear labels, and avoiding unnecessary visual clutter. The dashboard uses line charts for monthly trends "
            "and short interpretation boxes beside the data."
        ),
        "source": "Government Analysis Function - Data visualisation charts",
        "citation": "Government Analysis Function, n.d.",
        "url": "https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/",
    },
    {
        "decision": "AQI-style colour categories for public interpretation",
        "rationale": (
            "AirNow explains that AQI uses six colour-coded categories so people can quickly understand whether air quality "
            "is reaching unhealthy levels. The prototype uses this as an interpretation cue, not as a replacement for "
            "Malaysia-specific regulatory thresholds."
        ),
        "source": "AirNow - AQI Basics",
        "citation": "AirNow, n.d.",
        "url": "https://www.airnow.gov/aqi/aqi-basics/",
    },
    {
        "decision": "Source notes and caveats placed close to results",
        "rationale": (
            "Our World in Data air-pollution pages combine interactive charts with source context and public-health framing. "
            "The dashboard follows that pattern by keeping data coverage, source freshness, and limitations close to the "
            "charts instead of hiding them in technical documentation."
        ),
        "source": "Our World in Data - Air Pollution",
        "citation": "Our World in Data, n.d.",
        "url": "https://ourworldindata.org/air-pollution",
    },
]

DATA_SOURCE_REFERENCES = [
    {
        "decision": "Official baseline: OpenDOSM/DOE Monthly Air Pollution, 2017-01 to 2022-12",
        "rationale": (
            "The Malaysia open-data pollutant file is the official historical baseline used in this prototype. "
            "It supports historical comparison and short source-overlap checking, but it is not used as recent 2023-2026 PM evidence."
        ),
        "source": "OpenDOSM/Data.gov.my - Air Pollution",
        "citation": "Department of Statistics Malaysia and Department of Environment, n.d.",
        "url": "https://data.gov.my/data-catalogue/air_pollution",
    },
    {
        "decision": "Recent PM proxy: Open-Meteo Air Quality API using CAMS global modelled PM estimates, 2022-08 to 2026-06",
        "rationale": (
            "Open-Meteo provides PM2.5 and PM10 estimates from CAMS global atmospheric composition data. "
            "The dashboard labels this source as modelled proxy evidence for recent national PM trend screening and prototype forecasting."
        ),
        "source": "Open-Meteo - Air Quality API",
        "citation": "Open-Meteo, n.d.",
        "url": "https://open-meteo.com/en/docs/air-quality-api",
    },
    {
        "decision": "Climate context: NASA POWER monthly climate data, 2023-01 to 2025-12",
        "rationale": (
            "NASA POWER monthly climate data provide temperature, humidity, wind speed and rainfall context for the main "
            "2023-2025 project period. These variables are used as climate background, not as direct air-quality observations."
        ),
        "source": "NASA POWER Docs",
        "citation": "NASA POWER Project, n.d.",
        "url": "https://power.larc.nasa.gov/docs/",
    },
    {
        "decision": "Recent weather context: Open-Meteo Historical Weather, 2026-01 to 2026-06",
        "rationale": (
            "Open-Meteo Historical Weather extends current-year climate context for 2026. The daily weather values are "
            "aggregated into Malaysia-level monthly indicators for dashboard interpretation."
        ),
        "source": "Open-Meteo - Historical Weather API",
        "citation": "Open-Meteo, n.d.",
        "url": "https://open-meteo.com/en/docs/historical-weather-api",
    },
]

TERM_REFERENCES = [
    {
        "decision": "Explain PM2.5 and PM10 in plain language",
        "rationale": (
            "EPA defines PM as particle pollution and distinguishes PM10 as inhalable particles generally 10 micrometres "
            "and smaller, and PM2.5 as fine inhalable particles generally 2.5 micrometres and smaller. The dashboard uses "
            "that definition in chart notes."
        ),
        "source": "US EPA - Particulate Matter (PM) Basics",
        "citation": "U.S. Environmental Protection Agency, 2026",
        "url": "https://www.epa.gov/pm-pollution/particulate-matter-pm-basics",
    },
    {
        "decision": "Use NASA POWER climate data as contextual climate evidence",
        "rationale": (
            "NASA POWER provides technical documentation for data processing methodology and available web services. "
            "The dashboard therefore treats temperature, rainfall, wind speed and humidity as climate context rather "
            "than direct air-quality readings."
        ),
        "source": "NASA POWER Docs",
        "citation": "NASA POWER, 2026",
        "url": "https://power.larc.nasa.gov/docs/",
    },
]

MODEL_LABELS = {
    "naive": "Baseline forecast",
    "seasonal_naive": "Seasonal forecast",
    "arima": "ARIMA forecast",
    "prophet_additive": "Additive seasonal forecast",
    "random_forest": "Random Forest forecast",
}

MODEL_EXPLANATIONS = [
    (
        "Baseline forecast",
        "Uses the latest known PM value as the next forecast. It is included as the simplest comparison point.",
        "naive",
    ),
    (
        "Seasonal forecast",
        "Uses the same month from the previous year. It checks whether yearly haze or seasonal patterns help.",
        "seasonal_naive",
    ),
    (
        "ARIMA forecast",
        "Uses recent time-series movement to estimate the next months. It is a standard statistical forecasting model.",
        "arima",
    ),
    (
        "Additive seasonal forecast",
        "Combines a trend line with yearly seasonality. It is a transparent local model for comparison.",
        "prophet_additive",
    ),
    (
        "Random Forest forecast",
        "Uses lagged PM values and month-of-year signals to learn non-linear patterns from the historical series.",
        "random_forest",
    ),
]


@st.cache_data
def load_csv(path_text: str, mtime_ns: int) -> pd.DataFrame:
    frame = pd.read_csv(Path(path_text))
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"])
    return frame


def read_csv(path: Path) -> pd.DataFrame:
    return load_csv(str(path), path.stat().st_mtime_ns)


def friendly_variable(variable: str) -> str:
    return VARIABLE_LABELS.get(variable, variable)


def friendly_source(source: str) -> str:
    if source == "Open-Meteo CAMS global modelled PM":
        return "Estimated current PM data"
    if source == "OpenDOSM/DOE official baseline":
        return "Older official Malaysia data"
    if source == "NASA POWER monthly":
        return "Climate background data"
    if source == "Open-Meteo historical weather":
        return "Current-year climate data"
    return source


def icon_badge(kind: str) -> str:
    text = ICONS.get(kind, "•")
    color, background = ICON_STYLES.get(kind, ICON_STYLES["data"])
    return (
        f'<span class="section-icon" style="--icon-color:{color};'
        f'--icon-bg:{background};">{text}</span>'
    )


def title_case_heading(title: str) -> str:
    if not title:
        return title

    def convert_part(part: str) -> str:
        if not part or any(character.isupper() for character in part):
            return part
        return part[:1].upper() + part[1:]

    converted_words = []
    for word in title.split(" "):
        converted_words.append("-".join(convert_part(part) for part in word.split("-")))
    return " ".join(converted_words)


def render_section_heading(kind: str, title: str, level: int = 3) -> None:
    tag = "h4" if level == 4 else "h3"
    clean_title = title_case_heading(title)
    st.markdown(
        f"""
        <{tag} class="section-heading section-heading-{level}">
            {icon_badge(kind)}
            <span>{clean_title}</span>
        </{tag}>
        """,
        unsafe_allow_html=True,
    )


def variable_icon_kind(variable: str) -> str:
    return {
        "T2M": "temperature",
        "RH2M": "climate",
        "WS2M": "wind",
        "PRECTOTCORR": "rainfall",
        "PM2.5": "particles",
        "PM10": "particles",
    }.get(variable, "data")


def period_label(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "Not available"
    return f"{frame['date'].min().strftime('%Y-%m')} to {frame['date'].max().strftime('%Y-%m')}"


def status_for_row(row: pd.Series) -> str:
    end = pd.to_datetime(row["end_date"])
    if row["variable"] in AIR_POLLUTION_VARIABLES and end < ANALYSIS_START:
        return "Older official comparison data"
    if end >= ANALYSIS_START:
        return "Current project period"
    return "Historical"


def pm_category(variable: str, value: float) -> tuple[str, str]:
    for label, low, high, color in PM_BREAKPOINTS.get(variable, []):
        if low <= value < high:
            return label, color
    if variable in PM_BREAKPOINTS:
        return "Hazardous", "#7e0023"
    return "Not classified", "#8a9a5b"


def rainfall_category(value: float) -> tuple[str, str, str]:
    for label, low, high, color, meaning in RAINFALL_BANDS:
        if low <= value < high:
            return label, color, meaning
    label, _, _, color, meaning = RAINFALL_BANDS[-1]
    return label, color, meaning


def pm_band_frame(variable: str, max_value: float) -> pd.DataFrame:
    upper_limit = max(max_value * 1.2, 20.0 if variable == "PM2.5" else 80.0)
    rows = []
    for label, low, high, color in PM_BREAKPOINTS.get(variable, []):
        if low > upper_limit:
            continue
        rows.append(
            {
                "low": low,
                "high": min(high, upper_limit),
                "category": label,
                "color": color,
            }
        )
        if high >= upper_limit:
            break
    return pd.DataFrame(rows)


def relative_level(frame: pd.DataFrame, variable: str, value: float) -> tuple[str, str]:
    view = frame[frame["variable"] == variable].dropna(subset=["value"])
    if len(view) < 3:
        return "Not enough history", "More months are needed before comparing this value with its usual range."
    lower = float(view["value"].quantile(1 / 3))
    upper = float(view["value"].quantile(2 / 3))
    if value <= lower:
        return "Lower than usual", "This latest value sits in the lower third of values shown in the selected period."
    if value >= upper:
        return "Higher than usual", "This latest value sits in the higher third of values shown in the selected period."
    return "Middle range", "This latest value sits in the middle third of values shown in the selected period."


def latest_indicator_summary(frame: pd.DataFrame, variable: str) -> tuple[str, str, str]:
    view = frame[frame["variable"] == variable].sort_values("date")
    if view.empty:
        return "Not available", "No project-period data loaded", "No level available"
    latest = view.iloc[-1]
    value = f"{latest['value']:.2f} {VARIABLE_UNITS.get(variable, '')}".strip()
    if variable in PM_BREAKPOINTS:
        level, _ = pm_category(variable, float(latest["value"]))
        detail = f"{level} AQI-style guide for {latest['date'].strftime('%Y-%m')}"
        method = "Compared with public AQI-style PM concentration bands."
    elif variable == "PRECTOTCORR":
        level, _, _ = rainfall_category(float(latest["value"]))
        detail = f"{level} for {latest['date'].strftime('%Y-%m')}"
        method = "Compared with fixed monthly rainfall bands: below 100 mm is low, 100-200 mm is moderate, 200-300 mm is wet, and above 300 mm is very wet."
    else:
        level, method = relative_level(view, variable, float(latest["value"]))
        detail = f"{level} for {latest['date'].strftime('%Y-%m')}"
    return value, detail, method


def trend_summary(frame: pd.DataFrame, variable: str) -> dict[str, str]:
    view = frame[frame["variable"] == variable].sort_values("date")
    view = view.dropna(subset=["value"])
    if view.empty:
        return {
            "direction": "Not available",
            "latest": "Not available",
            "highest": "Not available",
            "lowest": "Not available",
            "meaning": "No data are available for this selected indicator and period.",
        }

    latest = view.iloc[-1]
    first = view.iloc[0]
    highest = view.loc[view["value"].idxmax()]
    lowest = view.loc[view["value"].idxmin()]
    unit = COMPACT_UNITS.get(variable, "")
    change = latest["value"] - first["value"]
    if abs(change) < 0.01:
        direction = "Stable across the selected period"
    elif change > 0:
        direction = "Higher than the first selected month"
    else:
        direction = "Lower than the first selected month"

    meaning = {
        "T2M": "For everyday users, higher temperature mainly means hotter outdoor conditions. It can also help explain why some pollution episodes feel more uncomfortable.",
        "RH2M": "Humidity means moisture in the air. High humidity can make the air feel heavier and may affect haze or visibility, even when it is not pollution by itself.",
        "WS2M": "Wind speed is important because moving air can spread particles away. When wind is weak, particles may remain around for longer.",
        "PRECTOTCORR": "Rainfall matters because rain can help wash particles from the air. A dry month may not get this natural cleaning effect.",
        "PM2.5": "Fine particles can enter deep into the lungs. In this dashboard, recent PM2.5 is a modelled estimate for national trend screening, not a direct station reading.",
        "PM10": "Coarse particles include dust and larger airborne particles. In this dashboard, recent PM10 is a modelled estimate for broad national pattern review.",
    }.get(variable, "This indicator provides supporting context for environmental trend interpretation.")

    return {
        "direction": direction,
        "latest": f"{latest['date'].strftime('%Y-%m')}: {latest['value']:.2f} {unit}".strip(),
        "highest": f"{highest['date'].strftime('%Y-%m')}: {highest['value']:.2f} {unit}".strip(),
        "lowest": f"{lowest['date'].strftime('%Y-%m')}: {lowest['value']:.2f} {unit}".strip(),
        "meaning": meaning,
    }


def render_source_note(source_label: str, status: str) -> None:
    st.markdown(
        f"""
        <div class="source-note">
            <span>{source_label}</span> - {status}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_note(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="info-note">
            <span class="info-icon">i</span>
            <div>
                <strong>{title}</strong>
                <p>{body}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_meaning_box(title: str, body: str, tone: str = "neutral") -> None:
    info_icon = ""
    if title == "What this means":
        info_icon = """
            <span class="hover-info" tabindex="0">i
                <span class="hover-info-text">
                    AI-assisted summary generated from the displayed data. Use it for interpretation support only and check it against the chart values and cited data sources.
                </span>
            </span>
        """
    st.markdown(
        f"""
        <div class="meaning-box meaning-{tone}">
            <strong class="meaning-title">{title}{info_icon}</strong>
            <span>{body}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_indicator_chart(frame: pd.DataFrame, variable: str, source_label: str, source_status: str) -> None:
    view = frame[frame["variable"] == variable]
    if view.empty:
        st.info(f"No data available for {friendly_variable(variable)} in the selected period.")
        return
    summary = trend_summary(view, variable)
    render_source_note(source_label, source_status)
    st.caption(
        f"{friendly_variable(variable)} ({VARIABLE_UNITS.get(variable, 'reported unit')}) - "
        f"{VARIABLE_EXPLANATIONS.get(variable, 'Supporting environmental indicator.')}"
    )
    chart_view = view.copy()
    chart_view["source_label"] = chart_view["source"].map(friendly_source)
    unit = COMPACT_UNITS.get(variable, "reported unit")
    y_title = f"Particle amount ({unit})" if variable in {"PM2.5", "PM10"} else unit
    if chart_view["source_label"].nunique() == 1:
        chart = (
            alt.Chart(chart_view)
            .mark_line(point=True, color="#176c5f", strokeWidth=3)
            .encode(
                x=alt.X("date:T", title="Month", axis=alt.Axis(format="%b %Y", labelAngle=-35)),
                y=alt.Y("value:Q", title=y_title, scale=alt.Scale(zero=False)),
                tooltip=[
                    alt.Tooltip("date:T", title="Month", format="%Y-%m"),
                    alt.Tooltip("value:Q", title=unit, format=".2f"),
                    alt.Tooltip("source_label:N", title="Source"),
                ],
            )
            .properties(height=280)
        )
        if variable in PM_BREAKPOINTS:
            bands = pm_band_frame(variable, float(chart_view["value"].max()))
            band_layer = (
                alt.Chart(bands)
                .mark_rect(opacity=0.13)
                .encode(
                    y=alt.Y("low:Q", title=y_title),
                    y2="high:Q",
                    color=alt.Color("category:N", scale=alt.Scale(domain=bands["category"].tolist(), range=bands["color"].tolist()), legend=None),
                    tooltip=[alt.Tooltip("category:N", title="AQI-style level")],
                )
            )
            chart = (band_layer + chart).resolve_scale(color="independent")
        elif variable not in PM_BREAKPOINTS:
            chart = (
                alt.Chart(chart_view)
                .mark_area(
                line={"color": "#176c5f", "strokeWidth": 3},
                color=alt.Gradient(
                    gradient="linear",
                    stops=[
                        alt.GradientStop(color="#d9eee9", offset=0),
                        alt.GradientStop(color="#ffffff", offset=1),
                    ],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                ),
                opacity=0.9,
                )
                .encode(
                    x=alt.X("date:T", title="Month", axis=alt.Axis(format="%b %Y", labelAngle=-35)),
                    y=alt.Y("value:Q", title=y_title, scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip("date:T", title="Month", format="%Y-%m"),
                        alt.Tooltip("value:Q", title=unit, format=".2f"),
                        alt.Tooltip("source_label:N", title="Source"),
                    ],
                )
                .properties(height=280)
            )
    else:
        chart = (
            alt.Chart(chart_view)
            .mark_line(point=True, strokeWidth=3)
            .encode(
                x=alt.X("date:T", title="Month", axis=alt.Axis(format="%b %Y", labelAngle=-35)),
                y=alt.Y("value:Q", title=y_title, scale=alt.Scale(zero=False)),
                color=alt.Color("source_label:N", title="Source"),
                tooltip=[
                    alt.Tooltip("date:T", title="Month", format="%Y-%m"),
                    alt.Tooltip("value:Q", title=unit, format=".2f"),
                    alt.Tooltip("source_label:N", title="Source"),
                ],
            )
            .properties(height=280)
        )
    st.altair_chart(chart, width="stretch")
    cols = st.columns(3)
    cols[0].metric("Period comparison", summary["direction"])
    cols[1].metric("Highest month", summary["highest"])
    cols[2].metric("Lowest month", summary["lowest"])
    if variable in {"PM2.5", "PM10"}:
        render_plain_language_note(
            "Period comparison",
            "This compares the first and latest month shown. It is not a health warning by itself.",
        )
    render_meaning_box("What this means", summary["meaning"])


def render_kpi_card(label: str, value: str, detail: str, tone: str = "neutral") -> None:
    st.markdown(
        f"""
        <div class="kpi-card kpi-{tone}">
            <span>{label}</span>
            <strong>{value}</strong>
            <p>{detail}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_explanation(label: str, method: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-explain">
            <strong>{label}</strong>
            <span>{method}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_plain_language_note(term: str, explanation: str) -> None:
    st.markdown(
        f"""
        <div class="plain-language-note">
            <strong>{term}</strong>
            <span>{explanation}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_inline_terms(variables_to_show: list[str]) -> None:
    for variable in variables_to_show:
        if variable in VARIABLE_EXPLANATIONS:
            render_plain_language_note(
                f"{friendly_variable(variable)} ({VARIABLE_UNITS.get(variable, 'reported unit')})",
                VARIABLE_EXPLANATIONS[variable],
            )


def render_daily_life_cards() -> None:
    cards = [
        (
            "Plan outdoor activity",
            "PM2.5 and PM10 show particle pollution. If the recent pattern is high or rising, sensitive users may choose shorter outdoor exercise or check official alerts before going out.",
            "pm",
        ),
        (
            "Understand rainy or calm days",
            "Rain can help wash particles from the air, while low wind can let pollution stay around longer. Climate data helps explain why air quality changes from month to month.",
            "climate",
        ),
        (
            "Read the forecast carefully",
            "The forecast is an early signal, not a guarantee. It helps users notice possible short-term changes and decide whether to monitor conditions more closely.",
            "neutral",
        ),
        (
            "Check official alerts",
            "Recent PM values are estimates for national trend screening. For health decisions, users should still check official air-quality advisories.",
            "neutral",
        ),
    ]
    columns = st.columns(4)
    for column, (title, body, tone) in zip(columns, cards):
        with column:
            st.markdown(
                f"""
                <div class="daily-card daily-{tone}">
                    <strong>{title}</strong>
                    <span>{body}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_data_meaning_cards() -> None:
    cards = [
        ("PM2.5", "Very small particles that can go deep into the lungs.", "Daily meaning: useful for breathing and sensitive-group awareness."),
        ("PM10", "Larger particles such as dust and coarse airborne particles.", "Daily meaning: useful for haze, dust and outdoor exposure awareness."),
        ("Rainfall", "How much rain occurred during the month.", "Daily meaning: rain can help remove particles from the air."),
        ("Wind speed", "How strongly air is moving.", "Daily meaning: stronger wind can disperse pollution; weak wind can let it stay around."),
        ("Temperature", "How warm the month was.", "Daily meaning: heat can influence air conditions and pollutant formation."),
        ("Humidity", "How much moisture is in the air.", "Daily meaning: moisture can affect haze, visibility and particle behaviour."),
    ]
    st.markdown('<div class="meaning-grid">', unsafe_allow_html=True)
    for title, definition, daily_meaning in cards:
        st.markdown(
            f"""
            <div class="data-meaning-card">
                <strong>{title}</strong>
                <span>{definition}</span>
                <p>{daily_meaning}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def chart_heading(variable: str) -> str:
    headings = {
        "T2M": "Temperature trend",
        "RH2M": "Humidity trend",
        "WS2M": "Wind speed trend",
        "PRECTOTCORR": "Rainfall trend",
        "PM2.5": "Fine particle (PM2.5) trend",
        "PM10": "Coarse particle (PM10) trend",
    }
    return headings.get(variable, f"{friendly_variable(variable)} trend")


def forecast_backtest(current_pm: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for variable in ["PM2.5", "PM10"]:
        view = current_pm[current_pm["variable"] == variable].sort_values("date")
        train = view[view["date"] <= pd.Timestamp("2025-12-01")]
        actual = view[(view["date"] >= pd.Timestamp("2026-01-01")) & (view["date"] <= pd.Timestamp("2026-06-01"))]
        if train.empty or actual.empty:
            continue
        naive_value = float(train.iloc[-1]["value"])
        seasonal_lookup = train.assign(month=train["date"].dt.month).set_index("month")["value"].to_dict()
        for model in ["naive", "seasonal_naive"]:
            predictions = []
            for _, row in actual.iterrows():
                if model == "naive":
                    predicted = naive_value
                else:
                    predicted = float(seasonal_lookup.get(row["date"].month, naive_value))
                predictions.append(predicted)
            errors = actual["value"].astype(float).reset_index(drop=True) - pd.Series(predictions)
            rows.append(
                {
                    "variable": variable,
                    "model": (
                        "Near-term baseline forecast"
                        if model == "naive"
                        else "Seasonal pattern forecast"
                    ),
                    "validation_period": "2026-01 to 2026-06",
                    "mae": float(errors.abs().mean()),
                    "rmse": float((errors.pow(2).mean()) ** 0.5),
                }
            )
    return pd.DataFrame(rows)


def render_forecast_chart(history: pd.DataFrame, forecast_frame: pd.DataFrame) -> None:
    if history.empty or forecast_frame.empty:
        return
    actual = history[history["variable"].isin(["PM2.5", "PM10"])][["date", "variable", "value"]].copy()
    actual["series"] = "Past estimated PM pattern"
    actual = actual.rename(columns={"value": "concentration"})
    future = forecast_frame[forecast_frame["variable"].isin(["PM2.5", "PM10"])][["date", "variable", "forecast", "model"]].copy()
    future["series"] = future["model"].map(MODEL_LABELS).fillna(future["model"])
    future = future.rename(columns={"forecast": "concentration"})
    combined = pd.concat(
        [actual[["date", "variable", "concentration", "series"]], future[["date", "variable", "concentration", "series"]]],
        ignore_index=True,
    )
    chart = (
        alt.Chart(combined)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("date:T", title="Month", axis=alt.Axis(format="%b %Y", labelAngle=-35)),
            y=alt.Y("concentration:Q", title="Particle amount (ug/m3)", scale=alt.Scale(zero=False)),
            color=alt.Color(
                "series:N",
                title="Line",
                legend=alt.Legend(orient="bottom", direction="horizontal", columns=3),
            ),
            strokeDash=alt.StrokeDash("series:N", title="Line", legend=None),
            column=alt.Column("variable:N", title=None),
            tooltip=[
                alt.Tooltip("date:T", title="Month", format="%Y-%m"),
                alt.Tooltip("variable:N", title="Indicator"),
                alt.Tooltip("concentration:Q", title="ug/m3", format=".2f"),
                alt.Tooltip("series:N", title="Line"),
            ],
        )
        .properties(height=270)
        .resolve_scale(y="independent")
    )
    st.altair_chart(chart, width="stretch")


def render_pm_comparison_chart(current_pm: pd.DataFrame) -> None:
    if current_pm.empty:
        return
    view = current_pm[current_pm["variable"].isin(["PM2.5", "PM10"])].copy()
    view["aqi_category"] = view.apply(lambda row: pm_category(row["variable"], float(row["value"]))[0], axis=1)
    line = (
        alt.Chart(view)
        .mark_line(strokeWidth=2.5, opacity=0.72)
        .encode(
            x=alt.X("date:T", title="Month", axis=alt.Axis(format="%b %Y", labelAngle=-35)),
            y=alt.Y("value:Q", title="Particle amount (ug/m3)", scale=alt.Scale(zero=False)),
            color=alt.Color(
                "variable:N",
                title="Particle type",
                scale=alt.Scale(domain=["PM2.5", "PM10"], range=["#176c5f", "#2b5f88"]),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Month", format="%Y-%m"),
                alt.Tooltip("variable:N", title="Indicator"),
                alt.Tooltip("value:Q", title="ug/m3", format=".2f"),
            ],
        )
        .properties(height=310)
    )
    points = (
        alt.Chart(view)
        .mark_circle(size=72, stroke="#ffffff", strokeWidth=1)
        .encode(
            x=alt.X("date:T", title="Month", axis=alt.Axis(format="%b %Y", labelAngle=-35)),
            y=alt.Y("value:Q", title="Particle amount (ug/m3)", scale=alt.Scale(zero=False)),
            color=alt.Color(
                "aqi_category:N",
                title="AQI-style level",
                scale=alt.Scale(
                    domain=[item[0] for item in AQI_CATEGORIES],
                    range=[item[2] for item in AQI_CATEGORIES],
                ),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Month", format="%Y-%m"),
                alt.Tooltip("variable:N", title="Indicator"),
                alt.Tooltip("value:Q", title="ug/m3", format=".2f"),
                alt.Tooltip("aqi_category:N", title="AQI-style level"),
            ],
        )
    )
    chart = (line + points).resolve_scale(color="independent")
    st.altair_chart(chart, width="stretch")


def render_aqi_scale() -> None:
    cells = ['<div class="aqi-scale">']
    for label, value_range, color, meaning in AQI_CATEGORIES:
        text_color = "#ffffff" if label in {"Very unhealthy", "Hazardous", "Unhealthy"} else "#111827"
        cells.append(
            f'<div class="aqi-cell" style="background:{color};color:{text_color};">'
            f"<strong>{label}</strong>"
            f"<span>{value_range}</span>"
            f"<p>{meaning}</p>"
            "</div>"
        )
    cells.append("</div>")
    st.markdown("".join(cells), unsafe_allow_html=True)


def render_rainfall_scale() -> None:
    cells = ['<div class="rainfall-scale">']
    for label, low, high, color, meaning in RAINFALL_BANDS:
        value_range = f"{int(low)}-{int(high)} mm" if high < 1000 else f"{int(low)}+ mm"
        cells.append(
            f'<div class="rain-cell" style="background:{color};">'
            f"<strong>{label}</strong>"
            f"<span>{value_range}</span>"
            f"<p>{meaning}</p>"
            "</div>"
        )
    cells.append("</div>")
    st.markdown("".join(cells), unsafe_allow_html=True)


def render_reference_items(references: list[dict[str, str]]) -> None:
    for reference in references:
        st.markdown(f"**{reference['decision']}**")
        st.write(reference["rationale"])
        st.markdown(f"Reference: [{reference['source']}]({reference['url']})")


def render_compact_reference_links(references: list[dict[str, str]]) -> None:
    for reference in references:
        st.markdown(
            f"- [{reference['source']}]({reference['url']}) "
            f"({reference['citation']})"
        )


def render_model_explanation() -> None:
    cards = ['<div class="model-grid">']
    for label, explanation, model_key in MODEL_EXPLANATIONS:
        cards.append(
            '<div class="model-card">'
            f'<strong>{icon_badge("forecast")}<span>{title_case_heading(label)}</span></strong>'
            f"<span>{explanation}</span>"
            "</div>"
        )
    cards.append("</div>")
    st.markdown("".join(cards), unsafe_allow_html=True)


def render_source_validation_section(source_validation: pd.DataFrame) -> None:
    render_section_heading("validation", "Official baseline vs modelled PM validation")
    st.write(
        "OpenDOSM/DOE official PM and Open-Meteo CAMS modelled PM overlap only from August 2022 to December 2022. This is a short directional check, not full validation."
    )
    if source_validation.empty:
        st.info("No source-validation table is available yet. Run the pipeline to generate `source_validation_summary.csv`.")
        return

    readable = source_validation.copy()
    readable["Official mean"] = pd.to_numeric(readable["official_mean"], errors="coerce").round(2)
    readable["Modelled mean"] = pd.to_numeric(readable["modelled_mean"], errors="coerce").round(2)
    readable["Mean difference"] = pd.to_numeric(readable["mean_bias_modelled_minus_official"], errors="coerce").round(2)
    readable["MAE"] = pd.to_numeric(readable["mae"], errors="coerce").round(2)
    readable["RMSE"] = pd.to_numeric(readable["rmse"], errors="coerce").round(2)
    readable["Correlation"] = pd.to_numeric(readable["correlation"], errors="coerce").round(2)
    display = readable.rename(
        columns={
            "variable": "Indicator",
            "overlap_months": "Overlap months",
            "overlap_period": "Overlap period",
            "status": "Status",
        }
    )[
        [
            "Indicator",
            "Overlap months",
            "Overlap period",
            "Official mean",
            "Modelled mean",
            "Mean difference",
            "MAE",
            "RMSE",
            "Correlation",
            "Status",
        ]
    ]
    st.dataframe(display, width="stretch", hide_index=True)
    render_plain_language_note(
        "How to read this validation",
        "Smaller error values are better. Positive mean difference means the modelled estimate is higher than the official baseline on average.",
    )


def render_design_rationale() -> None:
    render_section_heading("reference", "Design rationale and web references")
    st.write(
        "These references are included to show that the dashboard design choices are based on established public "
        "data-visualisation and service-design guidance, rather than arbitrary visual styling."
    )
    render_reference_items(DESIGN_REFERENCES)


def render_data_source_rationale() -> None:
    render_section_heading("baseline", "Official baseline and data-source references")
    st.write(
        "Source references used for data coverage and source labelling."
    )
    render_reference_items(DATA_SOURCE_REFERENCES)


def render_term_rationale() -> None:
    render_section_heading("reference", "Term definitions and citations")
    st.write(
        "The dashboard uses short, plain-language definitions beside charts so users do not need to leave the page "
        "to understand the main variables."
    )
    render_reference_items(TERM_REFERENCES)


st.markdown(
    """
    <style>
    :root {
        --ink: #0b1f1a;
        --muted: #35534b;
        --line: #cfe3da;
        --panel: #ffffff;
        --page: #eef7f2;
        --accent: #0f7a5a;
        --accent-soft: #dff3ea;
        --alert: #9a5b17;
        --alert-soft: #fff3df;
        --blue: #287a68;
        --sky-soft: #e2f0ec;
    }
    .stApp {
        background: var(--page);
        color: var(--ink);
    }
    #MainMenu,
    footer,
    header,
    [data-testid="stToolbar"] {
        visibility: hidden;
        height: 0;
    }
    .block-container {
        max-width: 1240px;
        padding-top: 1.2rem;
    }
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] * {
        color: var(--ink);
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: var(--ink) !important;
        font-weight: 650;
    }
    div[role="radiogroup"] {
        gap: 0.35rem;
        flex-wrap: wrap;
    }
    div[role="radiogroup"] label {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        padding: 7px 10px;
        margin-bottom: 5px;
        color: var(--ink) !important;
        font-weight: 720;
    }
    div[role="radiogroup"] label:hover {
        border-color: var(--accent);
        background: #eef7f4;
    }
    div[role="radiogroup"] label:has(input:checked) {
        border-color: var(--accent);
        background: var(--accent-soft);
    }
    .top-menu-title {
        color: var(--ink);
        font-size: 0.86rem;
        font-weight: 800;
        margin: 4px 0 2px;
    }
    h1, h2, h3, p {
        letter-spacing: 0;
        color: var(--ink);
    }
    .section-heading {
        display: flex;
        align-items: center;
        gap: 10px;
        color: var(--ink);
        font-weight: 780;
        line-height: 1.25;
        letter-spacing: 0;
        margin: 1.35rem 0 0.75rem;
    }
    .section-heading-3 {
        font-size: 1.12rem;
    }
    .section-heading-4 {
        font-size: 0.96rem;
        margin-top: 1.05rem;
    }
    .section-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        min-width: 30px;
        height: 30px;
        border-radius: 8px;
        border: 1px solid rgba(15, 122, 90, 0.24);
        background: var(--icon-bg);
        color: var(--icon-color);
        font-size: 1rem;
        font-weight: 860;
        font-variant-numeric: tabular-nums;
    }
    .section-heading-4 .section-icon {
        width: 25px;
        min-width: 25px;
        height: 25px;
        border-radius: 7px;
        font-size: 0.86rem;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--line);
        padding: 14px 16px;
    }
    div[data-testid="stMetric"] label {
        color: var(--muted);
    }
    .research-header {
        background:
            linear-gradient(135deg, rgba(15,122,90,0.14), rgba(93,127,50,0.10)),
            var(--panel);
        border: 1px solid var(--line);
        border-left: 6px solid var(--accent);
        padding: 24px 28px;
        margin-bottom: 18px;
    }
    .research-kicker {
        color: var(--accent);
        font-size: 0.78rem;
        font-weight: 760;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .research-title {
        color: var(--ink);
        font-size: 1.58rem;
        font-weight: 760;
        line-height: 1.25;
        margin-bottom: 8px;
    }
    .research-subtitle {
        color: var(--muted);
        font-size: 0.95rem;
        line-height: 1.5;
        max-width: 960px;
    }
    .prepared-by {
        color: #1f4f47;
        font-size: 0.86rem;
        font-weight: 720;
        margin-top: 10px;
    }
    .source-note {
        color: #475467;
        font-size: 0.82rem;
        font-style: italic;
        margin: 6px 0 4px;
    }
    .source-note span {
        color: var(--ink);
        font-weight: 650;
    }
    .info-note {
        display: grid;
        grid-template-columns: 28px 1fr;
        gap: 10px;
        align-items: start;
        background: #f8fafc;
        border: 1px solid var(--line);
        padding: 11px 13px;
        margin: 8px 0 16px;
        line-height: 1.4;
    }
    .info-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: var(--accent);
        color: #ffffff;
        font-weight: 800;
        font-size: 0.78rem;
    }
    .info-note strong {
        display: block;
        color: var(--ink);
        margin-bottom: 2px;
    }
    .info-note p {
        color: var(--muted);
        font-size: 0.84rem;
        margin: 0;
    }
    .status-band {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        margin: 8px 0 20px;
    }
    .status-card {
        background: var(--panel);
        border: 1px solid var(--line);
        padding: 13px 15px;
        min-height: 96px;
        transition: border-color 180ms ease, transform 180ms ease;
    }
    .status-card:hover {
        border-color: #9fb8b4;
        transform: translateY(-1px);
    }
    .status-card strong {
        display: block;
        font-size: 0.98rem;
        color: var(--ink);
        margin-bottom: 5px;
        line-height: 1.25;
    }
    .status-card span {
        display: block;
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.35;
    }
    .status-ready { border-top: 4px solid var(--accent); }
    .status-pending { border-top: 4px solid var(--alert); }
    .status-neutral { border-top: 4px solid var(--blue); }
    .note-box {
        background: var(--alert-soft);
        border: 1px solid #f3c47c;
        color: #673b00;
        padding: 14px 16px;
        margin: 10px 0 18px;
        line-height: 1.5;
    }
    .source-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0 18px;
    }
    .source-pill {
        border: 1px solid var(--line);
        background: var(--panel);
        padding: 8px 11px;
        font-size: 0.84rem;
        color: var(--ink);
    }
    .meaning-box {
        border: 1px solid var(--line);
        background: #ffffff;
        padding: 13px 15px;
        margin: 10px 0 18px;
        line-height: 1.48;
    }
    .meaning-box strong {
        display: flex;
        align-items: center;
        gap: 7px;
        color: var(--ink);
        margin-bottom: 4px;
    }
    .meaning-title {
        position: relative;
        width: max-content;
        max-width: 100%;
    }
    .hover-info {
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--accent);
        border: 2px solid #b4d9d0;
        color: #ffffff;
        font-size: 0.74rem;
        font-weight: 800;
        cursor: help;
        flex: 0 0 auto;
        box-shadow: 0 0 0 2px rgba(23, 108, 95, 0.08);
    }
    .hover-info-text {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        left: 24px;
        top: -8px;
        width: min(360px, 72vw);
        background: #f2fbf8;
        color: #0b3f37;
        border: 1px solid var(--accent);
        padding: 11px 13px;
        font-size: 0.8rem;
        line-height: 1.38;
        font-weight: 650;
        z-index: 20;
        transition: opacity 160ms ease;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.14);
    }
    .hover-info:hover .hover-info-text,
    .hover-info:focus .hover-info-text {
        visibility: visible;
        opacity: 1;
    }
    .meaning-box span {
        color: var(--muted);
    }
    .meaning-warning {
        border-color: #f3c47c;
        background: var(--alert-soft);
    }
    .meaning-success {
        border-color: #b4d9d0;
        background: #f2fbf8;
    }
    .scenario-box {
        border: 1px solid var(--line);
        background: #ffffff;
        border-left: 5px solid var(--blue);
        padding: 15px 17px;
        margin: 14px 0 18px;
    }
    .scenario-box strong {
        display: block;
        margin-bottom: 5px;
    }
    .kpi-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-bottom: 4px solid var(--blue);
        padding: 14px 16px;
        min-height: 152px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .kpi-card span {
        display: block;
        color: var(--muted);
        font-size: 0.78rem;
        font-weight: 750;
        margin-bottom: 7px;
    }
    .kpi-card strong {
        display: block;
        color: var(--ink);
        font-size: 1.36rem;
        font-variant-numeric: tabular-nums;
        line-height: 1.15;
        margin-bottom: 6px;
    }
    .kpi-card p {
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.35;
        margin: 0;
    }
    .kpi-explain {
        background: #ffffff;
        border: 1px solid var(--line);
        border-left: 4px solid #8a9a5b;
        padding: 10px 12px;
        margin: 8px 0;
        min-height: 116px;
        height: 100%;
    }
    .kpi-explain strong {
        display: block;
        color: var(--ink);
        font-size: 0.84rem;
        margin-bottom: 4px;
    }
    .kpi-explain span {
        color: var(--muted);
        font-size: 0.8rem;
        line-height: 1.35;
    }
    .kpi-pm {
        border-bottom-color: var(--accent);
        background: linear-gradient(180deg, #ffffff, #f3fbf8);
    }
    .kpi-climate {
        border-bottom-color: var(--blue);
        background: linear-gradient(180deg, #ffffff, #f4f8fb);
    }
    .plain-language-note {
        display: grid;
        grid-template-columns: 180px 1fr;
        gap: 12px;
        background: #ffffff;
        border: 1px solid var(--line);
        padding: 11px 13px;
        margin: 8px 0;
        line-height: 1.45;
    }
    .plain-language-note strong {
        color: var(--ink);
    }
    .plain-language-note span {
        color: var(--muted);
    }
    .daily-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-top: 4px solid var(--accent);
        padding: 14px 15px;
        min-height: 168px;
        line-height: 1.42;
    }
    .daily-card strong {
        display: block;
        color: var(--ink);
        font-size: 0.96rem;
        margin-bottom: 7px;
    }
    .daily-card span {
        color: var(--muted);
        font-size: 0.84rem;
    }
    .daily-climate {
        border-top-color: var(--blue);
    }
    .daily-neutral {
        border-top-color: #8a9a5b;
    }
    .meaning-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin: 10px 0 18px;
    }
    .data-meaning-card {
        background: #ffffff;
        border: 1px solid var(--line);
        padding: 13px 14px;
        min-height: 132px;
    }
    .data-meaning-card strong {
        display: block;
        color: var(--ink);
        margin-bottom: 5px;
    }
    .data-meaning-card span {
        display: block;
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.35;
        margin-bottom: 7px;
    }
    .data-meaning-card p {
        color: var(--ink);
        font-size: 0.84rem;
        line-height: 1.35;
        margin: 0;
    }
    .model-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(160px, 1fr));
        gap: 9px;
        margin: 10px 0 18px;
        overflow-x: auto;
        padding-bottom: 6px;
    }
    .model-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-top: 4px solid var(--accent);
        padding: 12px 13px;
        min-height: 154px;
        line-height: 1.36;
        min-width: 160px;
    }
    .model-card strong {
        display: flex;
        align-items: center;
        gap: 7px;
        color: var(--ink);
        font-size: 0.86rem;
        margin-bottom: 6px;
    }
    .model-card strong span {
        color: var(--ink);
        font-size: 0.86rem;
        line-height: 1.2;
    }
    .model-card span {
        display: block;
        color: var(--muted);
        font-size: 0.8rem;
    }
    .model-card strong span {
        display: inline;
        color: var(--ink);
        font-size: 0.86rem;
    }
    .model-card p {
        color: #667085;
        font-size: 0.74rem;
        margin: 7px 0 0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.18rem;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem;
    }
    .aqi-scale {
        display: grid;
        grid-template-columns: repeat(6, minmax(0, 1fr));
        gap: 6px;
        margin: 10px 0 18px;
    }
    .aqi-cell {
        color: #111827;
        padding: 10px 10px;
        font-size: 0.78rem;
        font-weight: 760;
        text-align: left;
        border: 1px solid rgba(0, 0, 0, 0.08);
        min-height: 116px;
    }
    .aqi-cell strong,
    .aqi-cell span,
    .aqi-cell p {
        display: block;
        color: inherit;
        margin: 0;
    }
    .aqi-cell strong {
        font-size: 0.86rem;
        margin-bottom: 3px;
    }
    .aqi-cell span {
        font-size: 0.78rem;
        margin-bottom: 6px;
    }
    .aqi-cell p {
        font-size: 0.74rem;
        line-height: 1.28;
        font-weight: 600;
    }
    .rainfall-scale {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 8px;
        margin: 10px 0 18px;
    }
    .rain-cell {
        color: #102033;
        padding: 11px 12px;
        min-height: 118px;
        border: 1px solid rgba(0, 0, 0, 0.08);
    }
    .rain-cell strong,
    .rain-cell span,
    .rain-cell p {
        display: block;
        color: inherit;
        margin: 0;
    }
    .rain-cell strong {
        font-size: 0.88rem;
        margin-bottom: 3px;
    }
    .rain-cell span {
        font-size: 0.8rem;
        font-weight: 750;
        margin-bottom: 6px;
    }
    .rain-cell p {
        font-size: 0.76rem;
        line-height: 1.3;
        font-weight: 600;
    }
    .readiness-list {
        border: 1px solid var(--line);
        background: var(--panel);
        margin: 8px 0 16px;
    }
    .readiness-step {
        display: grid;
        grid-template-columns: 34px 1fr auto;
        gap: 10px;
        align-items: center;
        padding: 13px 14px;
        border-bottom: 1px solid var(--line);
    }
    .readiness-step:last-child {
        border-bottom: 0;
    }
    .step-dot {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.82rem;
        color: #ffffff;
        background: var(--accent);
    }
    .step-dot.pending {
        background: var(--alert);
    }
    .step-title {
        font-weight: 760;
        color: var(--ink);
    }
    .step-detail {
        color: var(--muted);
        font-size: 0.88rem;
    }
    .step-tag {
        font-size: 0.78rem;
        font-weight: 760;
        color: var(--accent);
        background: var(--accent-soft);
        padding: 5px 8px;
    }
    .step-tag.pending {
        color: var(--alert);
        background: var(--alert-soft);
    }
    @media (max-width: 820px) {
        .status-band,
        .aqi-scale,
        .rainfall-scale {
            grid-template-columns: 1fr;
        }
        .plain-language-note {
            grid-template-columns: 1fr;
        }
        .meaning-grid {
            grid-template-columns: 1fr;
        }
        .readiness-step {
            grid-template-columns: 30px 1fr;
        }
        .step-tag {
            grid-column: 2;
            width: max-content;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <section class="research-header">
        <div class="research-kicker">Malaysia national dashboard prototype</div>
        <div class="research-title">{RESEARCH_TITLE}</div>
        <div class="research-subtitle">
            A local interactive dashboard for reviewing Malaysia climate indicators, estimated current-period PM2.5/PM10 patterns,
            and transparent short-term forecasting model comparisons.
        </div>
        <div class="prepared-by">Prepared by: Ng Hua Ching &nbsp; | &nbsp; Student ID: 22108471</div>
    </section>
    """,
    unsafe_allow_html=True,
)

PAGE_OPTIONS = [
    "Overview",
    "Climate Trends",
    "Air Quality & Forecasting",
    "Appendix",
]

st.markdown('<div class="top-menu-title">Dashboard menu</div>', unsafe_allow_html=True)
selected_page = st.radio(
    "Dashboard menu",
    PAGE_OPTIONS,
    horizontal=True,
    label_visibility="collapsed",
)

integrated_path = PROCESSED_DIR / "integrated_environment_monthly.csv"
coverage_path = TABLES_DIR / "data_coverage_summary.csv"
forecast_path = TABLES_DIR / "forecast_results.csv"
forecast_evaluation_path = TABLES_DIR / "forecast_evaluation.csv"
source_validation_path = TABLES_DIR / "source_validation_summary.csv"

if not integrated_path.exists():
    st.warning(
        "No processed dataset found. Run `python scripts/run_pipeline.py --download-public` "
        "and rerun the dashboard."
    )
    st.stop()

data = read_csv(integrated_path)
coverage = read_csv(coverage_path) if coverage_path.exists() else pd.DataFrame()
forecast = read_csv(forecast_path) if forecast_path.exists() else pd.DataFrame()
forecast_evaluation = read_csv(forecast_evaluation_path) if forecast_evaluation_path.exists() else pd.DataFrame()
source_validation = read_csv(source_validation_path) if source_validation_path.exists() else pd.DataFrame()

variables = sorted(data["variable"].dropna().unique().tolist())
sources = sorted(data["source"].dropna().unique().tolist())
current_period = data[data["date"] >= ANALYSIS_START]
preferred_default_variables = ["PM2.5", "PM10", "T2M", "PRECTOTCORR"]
default_variables = [variable for variable in preferred_default_variables if variable in current_period["variable"].unique()]
default_sources = sorted(current_period["source"].dropna().unique().tolist())
if not default_variables:
    default_variables = variables[: min(4, len(variables))]
if not default_sources:
    default_sources = sources

latest_available = data["date"].max()
default_end = min(latest_available, ANALYSIS_END)

current_pollution = current_period[current_period["variable"].isin(["PM2.5", "PM10"])]
baseline_pollution = data[(data["variable"].isin(AIR_POLLUTION_VARIABLES)) & (data["date"] < ANALYSIS_START)]
climate_context = current_period[current_period["variable"].isin(CLIMATE_VARIABLES)]

with st.sidebar:
    st.header("Filters")
    selected_dates = st.date_input(
        "Period shown",
        value=(ANALYSIS_START.date(), default_end.date()),
        min_value=data["date"].min().date(),
        max_value=latest_available.date(),
    )
    selected_variables = st.multiselect(
        "Indicators",
        variables,
        default=default_variables,
        format_func=friendly_variable,
    )
    selected_sources = st.multiselect("Data sources", sources, default=default_sources, format_func=friendly_source)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
else:
    start_date, end_date = ANALYSIS_START, default_end

filtered = data[
    data["variable"].isin(selected_variables)
    & data["source"].isin(selected_sources)
    & data["date"].between(start_date, end_date)
].copy()

climate_period = period_label(climate_context)
if current_pollution.empty:
    pm_card_class = "status-pending"
    pm_card_title = "Recent PM estimates needed"
    pm_card_detail = "Add estimated or observed 2023-2026 PM2.5/PM10 data before showing current air-quality forecasts."
else:
    pm_card_class = "status-ready"
    pm_sources = ", ".join(friendly_source(source) for source in sorted(current_pollution["source"].dropna().unique()))
    pm_card_title = "Recent PM estimates available"
    pm_card_detail = f"{pm_sources}: {period_label(current_pollution)}"
baseline_period = period_label(baseline_pollution)

if current_pollution.empty:
    st.markdown(
        """
        <div class="note-box">
            <strong>Important interpretation note:</strong>
            The dashboard does not claim current PM2.5/PM10 forecasting without valid 2023-2026 pollutant data.
            It separates older official comparison data from recent estimated PM data.
        </div>
        """,
        unsafe_allow_html=True,
    )

if selected_page == "Overview":
    render_section_heading("overview", "Malaysia air quality and climate overview")
    if current_pollution.empty:
        st.write(
            "At this stage, the dashboard can support climate trend review and historical air-quality baseline interpretation. "
            "Current PM2.5/PM10 analysis still needs a valid 2023-2026 pollutant source before forecast claims are made."
        )
    else:
        st.write(
            "The dashboard combines recent Malaysia climate conditions with estimated PM2.5/PM10 air-quality patterns "
            "and short-term forecast model comparisons."
        )

    render_section_heading("data", "Data currently shown")
    st.markdown(
        f"""
        <div class="status-band">
            <div class="status-card status-ready">
                <strong>Climate background data</strong>
                <span>Malaysia-level temperature, rainfall, wind and humidity context: {climate_period}</span>
            </div>
            <div class="status-card {pm_card_class}">
                <strong>{pm_card_title.replace("PM", "particulate matter (PM)")}</strong>
                <span>{pm_card_detail}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_daily_life_cards()

    render_section_heading("data", "Why these data matter")
    render_plain_language_note(
        "Why climate data matters",
        "Climate data does not directly say whether the air is safe. It helps explain the conditions around air quality. For example, rain can wash particles out of the air, while weak wind can allow pollution to stay around.",
    )
    render_plain_language_note(
        "Why particulate matter matters",
        "PM2.5 and PM10 describe particle pollution. They are useful because particles are one of the easiest air-quality risks for lay users to understand and monitor.",
    )
    render_plain_language_note(
        "How data helps daily life",
        "These trends can support awareness before outdoor activity, haze-sensitive planning, commuting, school activities and family decisions for people who may be sensitive to air pollution.",
    )

    render_section_heading("data", "Latest indicators")

    metric_cols = st.columns(4)
    overview_items = [
        ("PM2.5", current_pollution, "Fine particles", "pm"),
        ("PM10", current_pollution, "Coarse particles", "pm"),
        ("T2M", climate_context, "Temperature context", "climate"),
        ("PRECTOTCORR", climate_context, "Rainfall context", "climate"),
    ]
    overview_methods = []
    for column, (variable, frame, label, tone) in zip(metric_cols, overview_items):
        value, detail, method = latest_indicator_summary(frame, variable)
        overview_methods.append((label, method))
        with column:
            render_kpi_card(label, value, detail, tone)

    method_cols = st.columns(4)
    for column, (label, method) in zip(method_cols, overview_methods):
        with column:
            render_kpi_explanation(label, method)

    render_meaning_box(
        "How the low, middle or high label is decided",
        "For PM2.5 and PM10, the value is compared with public AQI-style particle concentration bands. For climate indicators, the latest value is compared with the values shown in this dashboard period: the lower third is treated as lower than usual, the middle third as middle range, and the upper third as higher than usual.",
        tone="success",
    )

    if not current_pollution.empty:
        render_section_heading("particles", "Current particulate matter (PM) pattern at a glance")
        render_inline_terms(["PM2.5", "PM10"])
        render_meaning_box(
            "Understanding micrograms per cubic metre",
            "The chart unit ug/m3 means micrograms per cubic metre. A microgram is a very small amount of mass; a cubic metre is a block of air about 1 metre wide, 1 metre long and 1 metre high. So the value estimates how much particle material is present in that amount of air (U.S. Environmental Protection Agency, 2026).",
        )
        render_pm_comparison_chart(current_pollution)
        render_plain_language_note(
            "Estimated PM data",
            "These values support trend awareness and forecasting demonstration. For health decisions, check official Malaysia air-quality advisories.",
        )
        if not forecast.empty and len(forecast.dropna(how="all")) > 0:
            render_section_heading("forecast", "Short-term particulate matter forecast")
            render_forecast_chart(current_pollution, forecast)

    render_meaning_box(
        "Example daily use",
        "If PM levels are rising and rain or wind is low, a user may choose to check official air-quality alerts before outdoor exercise, school activities, commuting or planning events.",
    )

elif selected_page == "Climate Trends":
    render_section_heading("climate", "Climate conditions that may affect air quality")
    climate_all = filtered[filtered["variable"].isin(CLIMATE_VARIABLES)]
    climate_years = sorted(climate_all["date"].dt.year.dropna().unique().tolist())
    climate_year = st.selectbox(
        "Climate year shown",
        climate_years,
        index=len(climate_years) - 1 if climate_years else 0,
        disabled=not climate_years,
    )
    climate_year_view = climate_all[climate_all["date"].dt.year == climate_year] if climate_years else climate_all
    st.caption(f"Showing monthly climate indicators for {climate_year}.")
    render_info_note(
        "Interpretation note",
        "Plain-language explanations are included to support public understanding. They are not medical advice, and any final health decision should still refer to official advisories and cited data sources.",
    )
    render_plain_language_note(
        "Quick reading guide",
        "Rain can help clear particles. Wind can disperse pollution. Hot and humid conditions can affect how particles behave and how uncomfortable the air feels.",
    )
    render_section_heading("rainfall", "Rainfall interpretation guide")
    render_rainfall_scale()
    render_inline_terms([variable for variable in ["PRECTOTCORR", "WS2M", "T2M", "RH2M"] if variable in selected_variables])
    if climate_year_view.empty:
        st.info("No climate indicators match the current filters.")
    else:
        for variable in [item for item in selected_variables if item in CLIMATE_VARIABLES]:
            render_section_heading(variable_icon_kind(variable), chart_heading(variable), level=4)
            render_indicator_chart(
                climate_year_view,
                variable,
                "Climate background data",
                "Satellite/reanalysis climate data used to describe Malaysia-level climate context",
            )

elif selected_page == "Air Quality & Forecasting":
    render_section_heading("air", "Air-quality particles and short-term forecast")
    air_years = sorted(current_pollution["date"].dt.year.dropna().unique().tolist())
    forecast_years = sorted(forecast["date"].dt.year.dropna().unique().tolist()) if not forecast.empty else []
    combined_air_years = sorted(set(air_years + forecast_years))
    air_year = st.selectbox(
        "Air-quality year shown",
        combined_air_years,
        index=len(combined_air_years) - 1 if combined_air_years else 0,
        disabled=not combined_air_years,
    )
    current_pollution_year = (
        current_pollution[current_pollution["date"].dt.year == air_year] if combined_air_years else current_pollution
    )
    forecast_year = forecast[forecast["date"].dt.year == air_year] if not forecast.empty and combined_air_years else forecast
    st.caption(f"Showing monthly PM trend and forecast for {air_year}.")
    if current_pollution_year.empty:
        render_meaning_box(
            "What this means",
            "This page shows whether recent PM2.5/PM10 data is available. Without recent PM data, the dashboard should not show current air-quality forecasts.",
            tone="warning",
        )
    else:
        render_meaning_box(
            "What this means",
            "This page shows recent particle-pollution patterns and simple short-term forecasts. Use it as an awareness tool, not as a replacement for official health alerts.",
            tone="success",
        )

    render_section_heading("air", "AQI-style interpretation scale")
    render_aqi_scale()
    render_plain_language_note(
            "AQI-style colours",
            "The colours help non-technical users read risk levels quickly. They are shown as a communication guide, not as a formal Malaysia regulatory classification.",
        )

    if not current_pollution_year.empty:
        render_inline_terms(["PM2.5", "PM10"])
        render_plain_language_note(
            "How this can help today",
            "If particle levels are higher than usual or the forecast points upward, sensitive users may choose lighter outdoor activity, check official advisories, or monitor conditions more closely.",
        )
        render_plain_language_note(
            "Why several forecast methods are shown",
            "Simple baseline forecasts are kept as comparison points. ARIMA, additive seasonal, and Random Forest are added so the dashboard can show whether advanced methods improve the short-term PM estimate.",
        )
        render_source_validation_section(source_validation)

        render_section_heading("particles", "Current-period PM pattern")
        render_section_heading("particles", "PM2.5 and PM10 overview trend", level=4)
        render_pm_comparison_chart(current_pollution_year)
        for variable in ["PM2.5", "PM10"]:
            render_section_heading(variable_icon_kind(variable), chart_heading(variable), level=4)
            render_indicator_chart(
                current_pollution_year,
                variable,
                "Estimated recent PM data",
                "Computer-model estimate for Malaysia-level trend screening, not direct station readings",
            )

        render_section_heading("forecast", "Forecast output")
        if forecast_year.empty or len(forecast_year.dropna(how="all")) == 0:
            st.info("Run the pipeline after loading current PM data to generate forecast outputs.")
        else:
            render_section_heading("forecast", "Forecast methods used", level=4)
            render_model_explanation()
            render_meaning_box(
                "How to read the forecast",
                "Use the forecast lines as comparison scenarios, not as guaranteed predictions. Baseline and seasonal forecasts are included because they show whether advanced models add value beyond simple assumptions. ARIMA, additive seasonal, and Random Forest add statistical and machine-learning comparison points.",
            )
            render_section_heading("forecast", "Short-term PM forecast trend", level=4)
            render_forecast_chart(current_pollution_year, forecast_year)
            validation = forecast_evaluation.copy()
            if not validation.empty:
                readable_validation = validation.copy()
                readable_validation["Average forecast error (MAE, ug/m3)"] = readable_validation["mae"].round(2)
                readable_validation["Large-error score (RMSE, ug/m3)"] = readable_validation["rmse"].round(2)
                readable_validation["model"] = readable_validation["model"].map(MODEL_LABELS).fillna(readable_validation["model"])
                readable_validation = readable_validation.rename(
                    columns={
                        "variable": "Indicator",
                        "model": "Forecast method",
                        "validation_period": "Checked against",
                    }
                )[
                    [
                        "Indicator",
                        "Forecast method",
                        "Checked against",
                        "n",
                        "Average forecast error (MAE, ug/m3)",
                        "Large-error score (RMSE, ug/m3)",
                    ]
                ]
                readable_validation = readable_validation.rename(columns={"n": "Months checked"})
                st.dataframe(readable_validation, width="stretch", hide_index=True)
                render_plain_language_note(
                    "Forecast error scores",
                    "Lower is better. Average forecast error (MAE) means the average miss. Large-error score (RMSE) is similar but gives extra penalty to larger mistakes.",
                )
            with st.expander("Show forecast values"):
                st.dataframe(forecast_year[forecast_year["variable"].isin(["PM2.5", "PM10"])], width="stretch", hide_index=True)

else:
    render_section_heading("appendix", "Appendix")
    st.write(
        "This appendix keeps the source details, validation caveats, and supporting references in one place."
    )

    render_section_heading("coverage", "Data sources and coverage")
    source_summary = pd.DataFrame(
        [
            {
                "Source role": "Official baseline",
                "Source": "OpenDOSM/DOE Monthly Air Pollution",
                "Coverage used": "2017-01 to 2022-12",
                "Main variables": "PM2.5, PM10 and other official pollutant indicators",
                "How it is used": "Historical baseline and short overlap check against modelled PM",
                "Reference": "https://data.gov.my/data-catalogue/air_pollution",
            },
            {
                "Source role": "Recent PM proxy",
                "Source": "Open-Meteo Air Quality API using CAMS global modelled PM estimates",
                "Coverage used": "2022-08 to 2026-06",
                "Main variables": "PM2.5 and PM10",
                "How it is used": "Recent national PM trend screening and prototype forecasting",
                "Reference": "https://open-meteo.com/en/docs/air-quality-api",
            },
            {
                "Source role": "Climate context",
                "Source": "NASA POWER monthly climate data",
                "Coverage used": "2023-01 to 2025-12",
                "Main variables": "Temperature, rainfall, humidity and wind speed",
                "How it is used": "Monthly climate background for interpreting environmental conditions",
                "Reference": "https://power.larc.nasa.gov/docs/",
            },
            {
                "Source role": "Recent weather context",
                "Source": "Open-Meteo Historical Weather",
                "Coverage used": "2026-01 to 2026-06",
                "Main variables": "Temperature, rainfall, humidity and wind speed",
                "How it is used": "Current-year weather context aggregated into monthly indicators",
                "Reference": "https://open-meteo.com/en/docs/historical-weather-api",
            },
        ]
    )
    st.dataframe(source_summary, width="stretch", hide_index=True)
    st.markdown(
        """
        The sources above are separated because official station observations, modelled PM estimates, and reanalysis weather data are different evidence types. Recent PM values are used for trend screening and prototype forecasting only, not as official Malaysia station observations.
        """
    )

    render_section_heading("coverage", "Detailed processed coverage table")
    if coverage.empty:
        st.info("Coverage summary has not been generated.")
    else:
        readable_coverage = coverage.copy()
        readable_coverage["indicator"] = readable_coverage["variable"].map(friendly_variable)
        readable_coverage["period"] = (
            pd.to_datetime(readable_coverage["start_date"]).dt.strftime("%Y-%m")
            + " to "
            + pd.to_datetime(readable_coverage["end_date"]).dt.strftime("%Y-%m")
        )
        readable_coverage["status"] = readable_coverage.apply(status_for_row, axis=1)
        readable_coverage["source_label"] = readable_coverage["source"].map(friendly_source)
        st.dataframe(
            readable_coverage[["indicator", "source_label", "period", "status", "missing_values"]].rename(
                columns={
                    "indicator": "Indicator",
                    "source_label": "Source",
                    "period": "Period",
                    "status": "Use in dashboard",
                    "missing_values": "Missing values",
                }
            ),
            width="stretch",
            hide_index=True,
        )

    render_source_validation_section(source_validation)

    render_section_heading("reference", "Supporting references")
    st.write(
        "These links support the source choices, term definitions, and dashboard design decisions used in this prototype."
    )
    st.markdown("**Data sources**")
    render_compact_reference_links(DATA_SOURCE_REFERENCES)
    st.markdown("**Term definitions**")
    render_compact_reference_links(TERM_REFERENCES)
    st.markdown("**Design references**")
    render_compact_reference_links(DESIGN_REFERENCES)

    render_section_heading("data", "Selected processed data preview")
    st.write(
        "This preview shows the latest rows from the processed Malaysia-level monthly dataset after source labelling and aggregation."
    )
    st.dataframe(filtered.tail(200), width="stretch", hide_index=True)

    render_section_heading("forecast", "Forecast output table")
    if forecast.empty or len(forecast.dropna(how="all")) == 0:
        st.info("Forecasts will appear after 2023+ PM2.5/PM10 CAMS data is added.")
    else:
        display_forecast = forecast[forecast["variable"].isin(selected_variables)] if selected_variables else forecast
        st.dataframe(display_forecast, width="stretch", hide_index=True)
