from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.common import read_jsonl, write_json


def load_keyed(records: list[dict[str, Any]], key_mode: str) -> dict[str, dict[str, Any]]:
    keyed: dict[str, dict[str, Any]] = {}
    for record in records:
        if key_mode == "id":
            key = str(record["id"])
        elif key_mode == "claim":
            key = str(record["claim"])
        elif key_mode == "claim_label":
            key = f"{record['claim']}|||{record.get('label', '')}"
        else:
            raise ValueError(f"Unsupported key mode: {key_mode}")
        keyed[key] = record
    return keyed


def main() -> None:
    parser = argparse.ArgumentParser(description="Check overlap between two FEVER subsets.")
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    left_records = read_jsonl(args.left)
    right_records = read_jsonl(args.right)
    summary: dict[str, Any] = {
        "left_size": len(left_records),
        "right_size": len(right_records),
        "comparisons": {},
    }
    for key_mode in ("id", "claim", "claim_label"):
        left_keyed = load_keyed(left_records, key_mode)
        right_keyed = load_keyed(right_records, key_mode)
        overlap_keys = sorted(set(left_keyed) & set(right_keyed))
        summary["comparisons"][key_mode] = {
            "overlap_count": len(overlap_keys),
            "overlap_ratio_vs_left": len(overlap_keys) / max(len(left_records), 1),
            "overlap_ratio_vs_right": len(overlap_keys) / max(len(right_records), 1),
            "overlap_items": [
                {
                    "key": key,
                    "left_id": str(left_keyed[key].get("id")),
                    "right_id": str(right_keyed[key].get("id")),
                    "claim": str(right_keyed[key].get("claim")),
                    "label": str(right_keyed[key].get("label", "")),
                    "primary_evidence_title": str(right_keyed[key].get("primary_evidence_title", "")),
                }
                for key in overlap_keys
            ],
        }
    write_json(args.output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
