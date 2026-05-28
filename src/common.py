from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

def project_root() -> Path:
    return Path(os.environ.get("CHRONORAG_ROOT", Path(__file__).resolve().parents[1]))


def ensure_dir(path: str | Path) -> Path:
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def write_jsonl(path: str | Path, items: list[dict[str, Any]]) -> None:
    target = Path(path)
    ensure_dir(target.parent)
    with target.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    ensure_dir(target.parent)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"JSON at {path} must contain a mapping at the top level.")
    return data


def read_yaml(path: str | Path) -> dict[str, Any]:
    import yaml

    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML at {path} must contain a mapping at the top level.")
    return data
