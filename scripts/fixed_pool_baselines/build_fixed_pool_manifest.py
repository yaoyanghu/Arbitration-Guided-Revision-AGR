from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from scripts.fixed_pool_baselines.common_io import write_json
from scripts.fixed_pool_baselines.manifest_utils import inspect_jsonl


DEFAULT_ROOT = Path("/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Freeze a read-only inventory of fixed-pool inputs and existing predictions.")
    parser.add_argument("--project-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    output = args.output or root / "outputs/published_baseline_adaptations_20260621/manifest/fixed_pool_manifest.json"
    entries: list[dict] = []
    fixed = {
        "dataset": [
            "data/processed/hoh_formal_1024.jsonl",
            "data/processed/temprageval_formal_1244.jsonl",
            "outputs/paper_assets_final/timeqa500_formal/timeqa500_examples.jsonl",
            "outputs/paper_assets_final/archivalqa500_formal/archivalqa500_examples.jsonl",
        ],
        "retrieval": [
            "runs/stageG_main_formal_hoh1024_20260414__full_model/retrieval_results.jsonl",
            "runs/stageG_main_formal_temprageval1244_20260414__full_model/retrieval_results.jsonl",
            "outputs/paper_assets_final/timeqa500_formal/retrieval_results.jsonl",
            "outputs/paper_assets_final/archivalqa500_formal/retrieval_results.jsonl",
        ],
    }
    for kind, paths in fixed.items():
        entries.extend(inspect_jsonl(root / relative, root, kind) for relative in paths)

    prediction_root = root / "outputs/aei_submission_closure_v1/predictions/strong_baselines"
    prefixes = ("tp_fp_rag_", "agr_", "fp_sr_", "fp_csr_", "fp_tsr_", "fp_easr_")
    for path in sorted(prediction_root.glob("*.jsonl")):
        if path.name.startswith(prefixes):
            entry = inspect_jsonl(path, root, "existing_prediction")
            entry["method_slug"] = next(prefix.rstrip("_") for prefix in prefixes if path.name.startswith(prefix))
            entries.append(entry)

    manifest = {
        "manifest_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(root),
        "policy": {
            "read_only_sources": True,
            "no_extra_retrieval": True,
            "no_index_rebuild": True,
            "gold_for_offline_evaluation_only": True,
        },
        "entry_count": len(entries),
        "all_required_exist": all(entry["exists"] for entry in entries),
        "all_required_readable": all(entry["readable"] for entry in entries),
        "entries": entries,
    }
    write_json(output, manifest)
    print(f"manifest={output} entries={len(entries)} readable={manifest['all_required_readable']}")


if __name__ == "__main__":
    main()
