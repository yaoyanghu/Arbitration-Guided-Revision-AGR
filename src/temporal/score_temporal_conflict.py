from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from src.common import read_jsonl, write_jsonl

UP_TO_DATE_CUES = ("as of", "current", "currently", "became", "joined", "launched", "is the", "is a")
STALE_CUES = ("former", "not yet", "before", "previously", "still", "had not yet")


def extract_query_year(query_text: str, query_time: Any) -> int | None:
    if query_time not in (None, ""):
        try:
            return int(query_time)
        except (TypeError, ValueError):
            pass
    years = re.findall(r"\b(?:19|20)\d{2}\b", query_text)
    return int(max(years)) if years else None


def evidence_year(record: dict[str, Any]) -> int | None:
    if record.get("evidence_time") not in (None, ""):
        try:
            return int(record["evidence_time"])
        except (TypeError, ValueError):
            pass
    text = f"{record.get('timestamp', '')} {record.get('text', '')}"
    years = re.findall(r"\b(?:19|20)\d{2}\b", text)
    return int(max(years)) if years else None


def score_temporal_record(record: dict[str, Any]) -> tuple[float, str]:
    query = str(record.get("query", ""))
    text = str(record.get("text", "")).lower()
    query_year = extract_query_year(query, record.get("query_time"))
    doc_year = evidence_year(record)

    if query_year is None or doc_year is None:
        return 0.5, "neutral_missing_year"

    if doc_year == query_year:
        score = 0.85
        reason = "exact_year_match"
    elif doc_year > query_year:
        score = 0.75
        reason = "newer_than_query"
    else:
        gap = query_year - doc_year
        score = max(0.05, 0.45 - 0.12 * gap)
        reason = "older_than_query"

    if any(cue in text for cue in UP_TO_DATE_CUES) and doc_year >= query_year:
        score += 0.1
        reason += "+update_cue"
    if any(cue in text for cue in STALE_CUES) and doc_year < query_year:
        score -= 0.1
        reason += "+stale_cue"

    temporal_status = str(record.get("temporal_status", "")).lower()
    if temporal_status == "updated":
        score += 0.1
        reason += "+updated_hint"
    elif temporal_status == "stale":
        score -= 0.1
        reason += "+stale_hint"
    elif temporal_status == "conflicting":
        score -= 0.05
        reason += "+conflict_hint"

    return max(0.0, min(1.0, score)), reason


def score_temporal_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for record in records:
        temporal_score, temporal_reason = score_temporal_record(record)
        enriched = dict(record)
        enriched["temporal_score"] = temporal_score
        enriched["temporal_reason"] = temporal_reason
        scored.append(enriched)
    return scored


def main() -> None:
    parser = argparse.ArgumentParser(description="Score Route A temporal-conflict candidates.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    records = read_jsonl(args.input)
    scored = score_temporal_records(records)
    write_jsonl(args.output, scored)
    print(json.dumps({"count": len(scored), "output": str(Path(args.output).resolve())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
