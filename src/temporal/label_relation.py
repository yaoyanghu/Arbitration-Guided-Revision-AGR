from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from src.common import read_jsonl, write_jsonl

YEAR_PATTERN = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")


def _extract_years(text: str) -> list[int]:
    return [int(item) for item in YEAR_PATTERN.findall(text)]


def _score_temporal(query_text: str, doc_text: str, timestamp: str) -> tuple[float, str]:
    query_years = _extract_years(query_text)
    doc_years = _extract_years(f"{doc_text} {timestamp}".strip())
    if not query_years or not doc_years:
        return 0.5, "neutral_missing_year"
    query_year = max(query_years)
    doc_year = max(doc_years)
    if doc_year == query_year:
        return 1.0, "exact_year_match"
    if doc_year > query_year:
        return 0.8, "newer_than_query"
    return 0.2, "older_than_query"


def score_temporal_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for record in records:
        temporal_score, temporal_relation = _score_temporal(
            query_text=str(record.get("query", "")),
            doc_text=str(record.get("text", "")),
            timestamp=str(record.get("timestamp", "")),
        )
        enriched = dict(record)
        enriched["temporal_score"] = temporal_score
        enriched["temporal_relation"] = temporal_relation
        scored.append(enriched)
    return scored


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply rule-based temporal scoring to retrieval results.")
    parser.add_argument("--input", required=True, help="Retrieval results jsonl.")
    parser.add_argument("--output", required=True, help="Output jsonl with temporal scores.")
    args = parser.parse_args()
    records = read_jsonl(args.input)
    scored = score_temporal_records(records)
    write_jsonl(args.output, scored)
    print(f"Wrote {len(scored)} temporal-scored records to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
