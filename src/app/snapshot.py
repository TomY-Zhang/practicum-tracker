import json
from datetime import UTC, datetime

from pandas import DataFrame

from app.config import SNAPSHOTS_DIR


class Snapshot:
    DATE_FORMAT = "%Y%m%d_%H%M%S"

    @classmethod
    def save(cls, df: DataFrame, changes: dict):
        now_utc = datetime.now(UTC).strftime(Snapshot.DATE_FORMAT)
        fname = f"{now_utc}.json"
        with open(SNAPSHOTS_DIR / fname, "w", encoding="utf-8") as file:
            data = {
                "dataframe": df.to_dict(orient="records"),
                "changes": changes,
            }
            json.dump(data, file, indent=4)

    @classmethod
    def get_latest(cls) -> dict:
        snapshots = {f for f in SNAPSHOTS_DIR.iterdir() if f.is_file()}
        if len(snapshots) == 0:
            return {}

        with open(max(snapshots), "r", encoding="utf-8") as file:
            return json.load(file)
