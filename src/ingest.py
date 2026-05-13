from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.config import (
    CSV_URL,
    GEOJSON_URL,
    RAW_CSV_PATH,
    RAW_GEOJSON_PATH,
    RAW_DIR,
    SOURCE_METADATA_PATH,
)


def download_file(url: str, destination: Path) -> dict:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    destination.write_bytes(response.content)
    return {
        "url": url,
        "path": str(destination),
        "bytes": len(response.content),
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def ingest() -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    metadata = {
        "dataset": "Ville de Montreal public EV charging stations",
        "resources": [
            download_file(CSV_URL, RAW_CSV_PATH),
            download_file(GEOJSON_URL, RAW_GEOJSON_PATH),
        ],
    }
    SOURCE_METADATA_PATH.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return metadata
