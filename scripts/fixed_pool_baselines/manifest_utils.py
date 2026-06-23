from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_jsonl(path: Path, project_root: Path, kind: str) -> dict[str, Any]:
    record: dict[str, Any] = {
        "absolute_path": str(path.resolve()),
        "relative_path": str(path.resolve().relative_to(project_root.resolve())),
        "kind": kind,
        "exists": path.exists(),
        "readable": False,
        "sha256": None,
        "row_count": 0,
        "schema_keys": [],
        "query_id_count": 0,
        "retrieval_rows_per_query_distribution": None,
        "error": None,
    }
    if not path.exists():
        return record
    try:
        query_counts: Counter[str] = Counter()
        first: dict[str, Any] | None = None
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"line {line_number}: expected object")
                record["row_count"] += 1
                first = first or row
                value = str(row.get("query_id", row.get("id", row.get("qid", "")))).strip()
                if value:
                    query_counts[value] += 1
        record["schema_keys"] = sorted(first.keys()) if first else []
        record["query_id_count"] = len(query_counts)
        if kind == "retrieval":
            distribution = Counter(query_counts.values())
            record["retrieval_rows_per_query_distribution"] = {
                str(rows_per_query): query_total for rows_per_query, query_total in sorted(distribution.items())
            }
        record["sha256"] = sha256_file(path)
        record["readable"] = True
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record
