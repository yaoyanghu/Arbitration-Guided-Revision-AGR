from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from src.common import ensure_dir, write_jsonl
from src.data.prepare_fever import normalize_record


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a disjoint FEVER validation subset by excluding tuning ids.")
    parser.add_argument("--raw-dev", required=True, help="Official FEVER shared_task_dev.jsonl path.")
    parser.add_argument("--tuning-predictions", required=True, help="500-query tuning predictions.jsonl path.")
    parser.add_argument("--output", required=True, help="Output disjoint validation jsonl.")
    parser.add_argument("--sample-size", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    tuning_rows = load_jsonl(args.tuning_predictions)
    tuning_ids = {str(row["id"]) for row in tuning_rows}
    raw_rows = load_jsonl(args.raw_dev)
    normalized = [normalize_record(row) for row in raw_rows]
    verifiable = [row for row in normalized if row.get("evidence_titles", row.get("evidence", []))]
    disjoint_pool = [row for row in verifiable if str(row["id"]) not in tuning_ids]
    if len(disjoint_pool) < args.sample_size:
        raise ValueError(f"Disjoint pool too small: {len(disjoint_pool)} < {args.sample_size}")
    subset = random.Random(args.seed).sample(disjoint_pool, args.sample_size)
    target = Path(args.output)
    ensure_dir(target.parent)
    write_jsonl(target, subset)
    print(
        json.dumps(
            {
                "tuning_size": len(tuning_ids),
                "verifiable_pool_size": len(verifiable),
                "disjoint_pool_size": len(disjoint_pool),
                "output_size": len(subset),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
