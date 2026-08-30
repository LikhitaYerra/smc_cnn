"""Record and replay simulation runs for comparison playback."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

RECORDINGS_DIR = "results/recordings"


def save_recording(states: list[dict], metadata: dict) -> str:
    os.makedirs(RECORDINGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode = metadata.get("controller_mode", "unknown")
    filename = f"{ts}_{mode}.json"
    path = os.path.join(RECORDINGS_DIR, filename)

    payload = {
        "metadata": metadata,
        "frames": states,
    }
    with open(path, "w") as f:
        json.dump(payload, f)

    return path


def list_recordings() -> list[dict]:
    if not os.path.isdir(RECORDINGS_DIR):
        return []

    recordings = []
    for fname in sorted(os.listdir(RECORDINGS_DIR), reverse=True):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(RECORDINGS_DIR, fname)
        try:
            with open(path) as f:
                data = json.load(f)
            meta = data.get("metadata", {})
            recordings.append({
                "id": fname.replace(".json", ""),
                "filename": fname,
                "controller_mode": meta.get("controller_mode", "?"),
                "scenario_name": meta.get("scenario_name", "?"),
                "frames": len(data.get("frames", [])),
                "metrics": meta.get("metrics", {}),
                "timestamp": meta.get("timestamp", ""),
            })
        except Exception:
            continue
    return recordings


def load_recording(recording_id: str) -> dict | None:
    path = os.path.join(RECORDINGS_DIR, f"{recording_id}.json")
    if not os.path.exists(path):
        path = os.path.join(RECORDINGS_DIR, recording_id)
        if not os.path.exists(path):
            return None
    with open(path) as f:
        return json.load(f)
