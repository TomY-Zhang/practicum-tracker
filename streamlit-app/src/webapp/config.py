import json
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    APP_ROOT = Path(getattr(sys, "_MEIPASS", os.getcwd()))
    WEBAPP_DIR = APP_ROOT
else:
    APP_ROOT = Path(__file__).resolve().parents[2]
    WEBAPP_DIR = APP_ROOT / "src" / "webapp"


ASSETS_DIR = APP_ROOT / "assets"
TEMPLATE_FILE_PATH = ASSETS_DIR / "template.pdf"
FIELD_MAP_PATH = ASSETS_DIR / "field_map.json"
GENERATED_PDF_NAME = "weekly_log.pdf"

with open(FIELD_MAP_PATH, "r") as file:
    FIELD_MAP = json.load(file)

DB_FILE_PATH = os.getenv("PRACTICUM_TRACKER_DB")
