from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

from scripts.fixed_pool_baselines.common_io import append_jsonl, read_jsonl
from scripts.fixed_pool_baselines.run_faithfulrag_fp import (
    classify_facts,
    clean_final_answer,
    faithful_answer_prompt,
    generate_batch,
)


ROOT = Path("/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG")
SOURCE = ROOT / "outputs/published_baseline_adaptations_20260621/predictions/faithfulrag_fp"
CONFIG = ROOT / "configs/fixed_pool/published_baseline_adaptations.yaml"


def recover_complete_fact_objects(text: str) -> list[dict[str, str]]:
    decoder = json.JSONDecoder()
    output: list[dict[str, str]] = []
    cursor = 0
    while cursor < len(text):
        start = text.find("{", cursor)
        if start < 0:
            break
        try:
            value, consumed = decoder.raw_decode(text[start:])
            if isinstance(value, dict) and "fact" in value and "classification" in value:
                output.append({str(key): str(item) for key, item in value.items()})
            cursor = start + consumed
        except json.JSONDecodeError:
            cursor = start + 1
    return output


def repair_key(dataset: str, row: dict[str, Any]) -> str:
    return f"{dataset}::{row['query_id']}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--dry-run", type=int, default=0)
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    if "nightly_closure_" not in str(output_root) or "fairness_repair" not in str(output_root):
        raise RuntimeError("output must stay under a nightly fairness_repair directory")
    output_root.mkdir(parents=True, exist_ok=True)
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    decoding = dict(config["decoding"])
    model_path = Path(config["models"]["primary_qwen"])

    candidates: list[tuple[str, dict[str, Any], list[dict[str, str]]]] = []
    unrecoverable = []
    for dataset in ("hoh", "temprageval", "timeqa"):
        rows = read_jsonl(SOURCE / f"faithfulrag_fp_{dataset}.jsonl")
        for row in rows:
            if str(row.get("parse_status", "")).lower() == "ok":
                continue
            facts = recover_complete_fact_objects(str(row.get("extraction_raw", "")))
            if facts:
                candidates.append((dataset, row, facts))
            else:
                unrecoverable.append({"dataset": dataset, "query_id": row["query_id"], "reason": "no_complete_fact_object_in_raw_output"})
    if args.dry_run:
        candidates = candidates[: args.dry_run]
        repair_file = output_root / "dryrun_repaired_rows.jsonl"
    else:
        repair_file = output_root / "repaired_rows.jsonl"
    done = {str(row["repair_key"]) for row in read_jsonl(repair_file)} if repair_file.exists() else set()
    pending = [item for item in candidates if repair_key(item[0], item[1]) not in done]
    if not pending:
        print(f"nothing pending; output={repair_file}")
        return

    seed = int(decoding["seed"])
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path), trust_remote_code=True, local_files_only=True, dtype=torch.bfloat16, device_map="auto"
    )
    model.eval()
    batch_size = int(decoding["batch_size"])
    for start in range(0, len(pending), batch_size):
        batch = pending[start:start + batch_size]
        prompts = []
        traces = []
        for dataset, row, facts in batch:
            supported, contradicted, neutral = classify_facts(facts)
            prompts.append(faithful_answer_prompt(tokenizer, str(row["question"]), supported, contradicted, neutral))
            traces.append((dataset, row, facts, supported, contradicted, neutral))
        outputs = generate_batch(model, tokenizer, prompts, decoding)
        repaired = []
        for trace, answer_output in zip(traces, outputs):
            dataset, original, facts, supported, contradicted, neutral = trace
            final_answer, answer_parse = clean_final_answer(answer_output["text"])
            row = dict(original)
            row.update({
                "repair_key": repair_key(dataset, original),
                "extracted_facts": facts, "supported_facts": supported,
                "contradicted_facts": contradicted, "neutral_facts": neutral,
                "fact_count": len(facts), "supported_count": len(supported),
                "contradicted_count": len(contradicted),
                "answer_raw": answer_output["text"], "final_answer": final_answer,
                "answer_changed": final_answer.strip() != str(original["initial_answer"]).strip(),
                "revision_applied": final_answer.strip() != str(original["initial_answer"]).strip(),
                "input_tokens_answer": answer_output["input_tokens"],
                "output_tokens_answer": answer_output["output_tokens"],
                "total_input_tokens": int(original["input_tokens_extraction"]) + answer_output["input_tokens"],
                "total_output_tokens": int(original["output_tokens_extraction"]) + answer_output["output_tokens"],
                "latency_answer_sec": answer_output["latency_sec"],
                "total_latency_sec": float(original["latency_extraction_sec"]) + answer_output["latency_sec"],
                "latency_sec": float(original["latency_extraction_sec"]) + answer_output["latency_sec"],
                "parse_status": "ok" if answer_parse == "ok" else answer_parse,
                "parsing_failure": answer_parse != "ok",
                "extraction_parse_repair": "recovered_complete_objects_from_truncated_or_wrapped_json",
                "no_extra_retrieval": True,
            })
            repaired.append(row)
        append_jsonl(repair_file, repaired)
        print(f"progress={min(start + len(batch), len(pending))}/{len(pending)}")
    (output_root / "unrecoverable_rows.json").write_text(json.dumps(unrecoverable, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"complete repaired={len(candidates)} unrecoverable={len(unrecoverable)} output={repair_file}")


if __name__ == "__main__":
    main()
