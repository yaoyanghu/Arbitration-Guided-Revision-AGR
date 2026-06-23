from __future__ import annotations

import json
from pathlib import Path

import yaml

from scripts.fixed_pool_baselines.evidence_formatting import evidence_ids, format_evidence
from scripts.fixed_pool_baselines.fixed_pool_schema import gold_answers, predicted_answer, query_id
from scripts.fixed_pool_baselines.metrics import metric_payload


ROOT = Path("/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG")


def main() -> None:
    assert query_id({"id": "x"}) == "x"
    assert query_id({"query_id": 3}) == "3"
    assert gold_answers({"gold_answer": "West German"}) == ["West German"]
    assert predicted_answer({"final_answer": "A"}) == "A"
    assert metric_payload("The Answer", ["the answer"])["EM"] == 1.0
    evidence = [{"doc_id": "d1", "title": "T", "timestamp": "2024", "text": "Evidence text"}]
    assert evidence_ids(evidence) == ["d1"]
    assert "Evidence text" in format_evidence(evidence)
    manifest = json.loads((ROOT / "outputs/published_baseline_adaptations_20260621/manifest/fixed_pool_manifest.json").read_text(encoding="utf-8"))
    assert manifest["all_required_exist"] is True
    assert manifest["all_required_readable"] is True
    assert manifest["entry_count"] >= 29
    config = yaml.safe_load((ROOT / "configs/fixed_pool/published_baseline_adaptations.yaml").read_text(encoding="utf-8"))
    assert config["fixed_pool"]["allow_extra_retrieval"] is False
    assert config["fixed_pool"]["allow_gold_in_prompt"] is False
    print("foundation smoke test: PASS")


if __name__ == "__main__":
    main()
