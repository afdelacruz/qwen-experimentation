from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def infer_category(video_path: Path) -> str | None:
    """Infer a category from the parent directory name when possible."""
    if not video_path.parent.name:
        return None
    return video_path.parent.name or None


def ensure_parent_dir(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)


def write_json(output_path: Path, payload: dict[str, Any]) -> None:
    ensure_parent_dir(output_path)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
