import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
APP_ROOT = REPO_ROOT / "src" / "app"
ASSETS_PATH = REPO_ROOT / "assets"
TEMPLATE_FILE_PATH = ASSETS_PATH / "template.pdf"
FIELD_MAP_PATH = ASSETS_PATH / "field_map.json"
GENERATED_PDF_NAME = "weekly_log.pdf"

with open(FIELD_MAP_PATH, "r") as file:
    FIELD_MAP = json.load(file)

DB_FILE_PATH = os.getenv("PRACTICUM_TRACKER_DB")
