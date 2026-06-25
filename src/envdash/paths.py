from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"
REPORTS_DIR = PROJECT_ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FIGURES_DIR = REPORTS_DIR / "figures"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"


def ensure_project_dirs() -> None:
    for path in [
        CONFIG_DIR,
        RAW_DIR / "opendosm",
        RAW_DIR / "nasa_power",
        RAW_DIR / "cams",
        INTERIM_DIR,
        PROCESSED_DIR,
        METADATA_DIR,
        TABLES_DIR,
        FIGURES_DIR,
        MODELS_DIR,
        LOGS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
