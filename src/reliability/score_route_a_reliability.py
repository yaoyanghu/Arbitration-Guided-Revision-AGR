from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.common import read_jsonl, write_jsonl

SOURCE_TYPE_PRIORS = {
    "official_record": 1.0,
    "encyclopedic_current": 0.9,
    "structured_kb": 0.85,
    "news_report": 0.78,
    "archival_news": 0.65,
    "blog": 0.4,
    "unknown": 0.5,
}


def reliability_score(record: dict) -> tuple[float, str]:
    source_type = str(record.get("source_type", "")).strip().lower() or "unknown"
    if source_type in SOURCE_TYPE_PRIORS:
        return SOURCE_TYPE_PRIORS[source_type], source_type
    source = str(record.get("source", "")).lower()
    for key, value in SOURCE_TYPE_PRIORS.items():
        if key in source:
            return value, key
    return SOURCE_TYPE_PRIORS["unknown"], "unknown"


def score_reliability_records(records: list[dict]) -> list[dict]:
    scored: list[dict] = []
    for record in records:
        score, bucket = reliability_score(record)
        enriched = dict(record)
        enriched["reliability_score"] = score
        enriched["reliability_bucket"] = bucket
        scored.append(enriched)
    return scored


def main() -> None:
    parser = argparse.ArgumentParser(description="Score Route A reliability priors.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    records = read_jsonl(args.input)
    scored = score_reliability_records(records)
    write_jsonl(args.output, scored)
    print(json.dumps({"count": len(scored), "output": str(Path(args.output).resolve())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
