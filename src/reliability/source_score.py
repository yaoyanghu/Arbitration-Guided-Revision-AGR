from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from src.common import read_jsonl, write_jsonl

SOURCE_PRIORS = {
    "wikipedia": 1.0,
    "wikidata": 0.85,
    "gov": 0.9,
    "government": 0.9,
    "news": 0.8,
    "academic": 0.95,
    "journal": 0.95,
    "blog": 0.4,
    "forum": 0.3,
    "unknown": 0.5,
}


def _score_source(source: str) -> tuple[float, str]:
    normalized = source.strip().lower() or "unknown"
    for key, value in SOURCE_PRIORS.items():
        if key in normalized:
            return value, key
    return SOURCE_PRIORS["unknown"], "unknown"


def score_reliability_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for record in records:
        reliability_score, reliability_bucket = _score_source(str(record.get("source", "unknown")))
        enriched = dict(record)
        enriched["reliability_score"] = reliability_score
        enriched["reliability_bucket"] = reliability_bucket
        scored.append(enriched)
    return scored


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply rule-based source reliability scoring.")
    parser.add_argument("--input", required=True, help="Input jsonl.")
    parser.add_argument("--output", required=True, help="Output jsonl with reliability scores.")
    args = parser.parse_args()
    records = read_jsonl(args.input)
    scored = score_reliability_records(records)
    write_jsonl(args.output, scored)
    print(f"Wrote {len(scored)} reliability-scored records to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
