import json
from pathlib import Path
from typing import Any

from .paths import CONFIG_DIR


def load_json_config(filename: str) -> dict[str, Any]:
    path = Path(filename)
    if not path.is_absolute():
        path = CONFIG_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
