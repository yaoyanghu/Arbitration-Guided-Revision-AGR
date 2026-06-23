from __future__ import annotations

import argparse
import json
import random
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

from scripts.fixed_pool_baselines.common_io import append_jsonl, read_jsonl
from scripts.fixed_pool_baselines.evidence_formatting import evidence_ids, format_evidence
from scripts.fixed_pool_baselines.fixed_pool_schema import gold_answers, predicted_answer, query_id, question_text
from scripts.fixed_pool_baselines.manifest_utils import sha256_file
from scripts.fixed_pool_baselines.runtime_logging import RunLogger


DEFAULT_CONFIG = Path("configs/fixed_pool/published_baseline_adaptations.yaml")
PROMPT_VERSION = "self_refine_fp_v1_20260621"
ALLOWED_FEEDBACK_STATUS = {"acceptable", "unsupported", "stale", "relation_mismatched"}

FEEDBACK_SYSTEM = (
    "You are the feedback component of a Self-Refine QA system. Inspect only the supplied question, "
    "fixed evidence, and initial answer. Do not use outside knowledge. Do not propose a final answer."
)
FEEDBACK_INSTRUCTION = """Assess the initial answer against the fixed evidence and the question's temporal and relation constraints.
Return exactly one compact JSON object with this schema:
{"status":"acceptable|unsupported|stale|relation_mismatched","feedback":"concise actionable critique"}
Use acceptable only when the initial answer is adequately supported and satisfies the requested relation/time. Do not include a final answer."""

REFINEMENT_SYSTEM = (
    "You are the refinement component of a Self-Refine QA system. Use only the supplied fixed evidence, "
    "initial answer, and self-feedback. Return a short final answer and no explanation."
)
REFINEMENT_INSTRUCTION = """Refine the initial answer using the self-feedback and only the fixed evidence.
If the feedback says acceptable, keep the initial answer. Otherwise revise only when the fixed evidence supports the change.
If the fixed evidence is insufficient, output "Insufficient evidence". Return the shortest final answer string only."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Self-Refine-FP with frozen evidence and an existing TP-FP initial answer.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--dataset", required=True, choices=("hoh", "temprageval", "timeqa", "archivalqa"))
    parser.add_argument("--dry-run", type=int, default=0, metavar="N")
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    return parser.parse_args()


def lookup(config: dict[str, Any], dotted: str) -> Any:
    value: Any = config
    for part in dotted.split("."):
        value = value[part]
    return value


def resolve_config_node(value: Any, config: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        return {key: resolve_config_node(item, config) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve_config_node(item, config) for item in value]
    if not isinstance(value, str):
        return value
    pattern = re.compile(r"\$\{([^}]+)\}")
    previous = None
    while previous != value:
        previous = value
        value = pattern.sub(lambda match: str(lookup(config, match.group(1))), value)
    return value


def load_config(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    # Resolve in two passes because output_root itself references project.root.
    first = resolve_config_node(raw, raw)
    return resolve_config_node(first, first)


def group_retrieval(path: Path, top_k: int) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in read_jsonl(path):
        grouped[str(row.get("query_id", ""))].append(row)
    for value, rows in grouped.items():
        rows.sort(key=lambda row: int(row.get("rank", 10**9)))
        grouped[value] = rows[:top_k]
    return dict(grouped)


def prediction_map(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(path):
        value = query_id(row)
        if not value or value in result:
            raise ValueError(f"missing/duplicate query_id in {path}: {value!r}")
        result[value] = row
    return result


def verify_frozen_inputs(root: Path, paths: list[Path]) -> None:
    manifest_path = root / "outputs/published_baseline_adaptations_20260621/manifest/fixed_pool_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {entry["absolute_path"]: entry for entry in manifest["entries"]}
    for path in paths:
        resolved = str(path.resolve())
        if resolved not in expected:
            raise RuntimeError(f"input is not frozen in manifest: {resolved}")
        entry = expected[resolved]
        if not entry["readable"] or sha256_file(path) != entry["sha256"]:
            raise RuntimeError(f"manifest hash/readability check failed: {resolved}")


def feedback_prompt(tokenizer, question: str, evidence: list[dict[str, Any]], initial_answer: str) -> str:
    user = (
        f"Question:\n{question}\n\nFixed evidence pool:\n{format_evidence(evidence)}\n\n"
        f"Initial TP-FP answer:\n{initial_answer}\n\nInstruction:\n{FEEDBACK_INSTRUCTION}"
    )
    return tokenizer.apply_chat_template(
        [{"role": "system", "content": FEEDBACK_SYSTEM}, {"role": "user", "content": user}],
        tokenize=False,
        add_generation_prompt=True,
    )


def refinement_prompt(
    tokenizer, question: str, evidence: list[dict[str, Any]], initial_answer: str, feedback_text: str, feedback_status: str
) -> str:
    user = (
        f"Question:\n{question}\n\nFixed evidence pool:\n{format_evidence(evidence)}\n\n"
        f"Initial TP-FP answer:\n{initial_answer}\n\nSelf-feedback status: {feedback_status}\n"
        f"Self-feedback:\n{feedback_text}\n\nInstruction:\n{REFINEMENT_INSTRUCTION}\n\nFinal answer:"
    )
    return tokenizer.apply_chat_template(
        [{"role": "system", "content": REFINEMENT_SYSTEM}, {"role": "user", "content": user}],
        tokenize=False,
        add_generation_prompt=True,
    )


def generate_batch(model, tokenizer, prompts: list[str], decoding: dict[str, Any]) -> list[dict[str, Any]]:
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    device = next(model.parameters()).device
    encoded = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True, max_length=3072).to(device)
    input_counts = encoded.attention_mask.sum(dim=1).tolist()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    started = time.perf_counter()
    with torch.inference_mode():
        generated = model.generate(
            **encoded,
            max_new_tokens=int(decoding["max_new_tokens"]),
            do_sample=True,
            temperature=float(decoding["temperature"]),
            top_p=float(decoding["top_p"]),
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    latency_each = (time.perf_counter() - started) / max(len(prompts), 1)
    input_width = encoded.input_ids.shape[1]
    outputs = []
    for index in range(len(prompts)):
        tokens = generated[index][input_width:]
        valid = tokens[tokens != tokenizer.pad_token_id]
        outputs.append({
            "text": tokenizer.decode(valid, skip_special_tokens=True).strip(),
            "input_tokens": int(input_counts[index]),
            "output_tokens": int(valid.numel()),
            "latency_sec": latency_each,
        })
    return outputs


def parse_feedback(text: str) -> tuple[str, str, str]:
    cleaned = re.sub(r"<\|.*?\|>", " ", text).strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.S)
    if match:
        try:
            value = json.loads(match.group(0))
            status = str(value.get("status", "")).strip().lower()
            feedback = str(value.get("feedback", "")).strip()
            if status in ALLOWED_FEEDBACK_STATUS and feedback:
                return status, feedback, "ok"
        except json.JSONDecodeError:
            pass
    fallback = " ".join(cleaned.split())[:1000] or "Feedback output was empty; reassess support conservatively."
    return "unknown", fallback, "feedback_parse_fallback"


def clean_final_answer(text: str) -> tuple[str, str]:
    cleaned = re.sub(r"<\|.*?\|>", " ", str(text)).strip()
    cleaned = cleaned.splitlines()[0].strip() if cleaned else ""
    cleaned = re.sub(r"^(final answer|answer)\s*[:\-]\s*", "", cleaned, flags=re.I).strip(" \t\"'`")
    if not cleaned:
        return "Insufficient evidence", "refinement_empty_fallback"
    if len(cleaned.split()) > 32:
        return " ".join(cleaned.split()[:32]), "refinement_truncated"
    return cleaned, "ok"


def write_prompt_archive(output_root: Path) -> None:
    target = output_root / "prompts/self_refine_fp_v1.md"
    content = (
        "# Self-Refine-FP Prompt Archive\n\n"
        f"Prompt version: `{PROMPT_VERSION}`\n\n## Feedback system\n\n{FEEDBACK_SYSTEM}\n\n"
        f"## Feedback instruction\n\n{FEEDBACK_INSTRUCTION}\n\n## Refinement system\n\n{REFINEMENT_SYSTEM}\n\n"
        f"## Refinement instruction\n\n{REFINEMENT_INSTRUCTION}\n"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_text(encoding="utf-8") != content:
        raise RuntimeError(f"prompt archive drift: {target}")
    if not target.exists():
        target.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    root = Path(config["project"]["root"])
    output_root = Path(config["project"]["output_root"])
    dataset = config["datasets"][args.dataset]
    decoding = dict(config["decoding"])
    if args.batch_size:
        decoding["batch_size"] = args.batch_size
    queries_path = Path(dataset["queries"])
    retrieval_path = Path(dataset["retrieval"])
    initial_path = Path(dataset["tp_fp"])
    verify_frozen_inputs(root, [queries_path, retrieval_path, initial_path])
    write_prompt_archive(output_root)

    default_name = f"dryrun_{args.dataset}.jsonl" if args.dry_run else f"self_refine_fp_{args.dataset}.jsonl"
    output_path = args.output or output_root / "predictions/self_refine_fp" / default_name
    if output_root.resolve() not in output_path.resolve().parents:
        raise RuntimeError(f"output must stay under the new adaptation root: {output_root}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = "_dryrun" if args.dry_run else ""
    logger = RunLogger(output_root / f"logs/self_refine_fp_{args.dataset}{suffix}.log")

    queries = read_jsonl(queries_path)
    if args.dry_run:
        queries = queries[: args.dry_run]
    retrieval = group_retrieval(retrieval_path, int(config["fixed_pool"]["generation_evidence_top_k"]))
    initial = prediction_map(initial_path)
    done = {query_id(row) for row in read_jsonl(output_path)} if output_path.exists() else set()
    pending = [row for row in queries if query_id(row) not in done]
    logger.log(f"dataset={args.dataset} total={len(queries)} done={len(done)} pending={len(pending)} output={output_path}")
    if args.preflight_only:
        logger.log("preflight complete; model was not loaded")
        return
    if not pending:
        return

    seed = int(decoding["seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    model_path = Path(config["models"]["primary_qwen"])
    logger.log(f"loading model={model_path}")
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path), trust_remote_code=True, local_files_only=True, dtype=torch.bfloat16, device_map="auto"
    )
    model.eval()
    logger.log(f"model loaded cuda={torch.cuda.is_available()} gpu={torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none'}")

    batch_size = int(decoding["batch_size"])
    for start in range(0, len(pending), batch_size):
        batch = pending[start : start + batch_size]
        contexts = []
        feedback_prompts = []
        for query_row in batch:
            value = query_id(query_row)
            if value not in initial:
                raise RuntimeError(f"TP-FP answer missing for {value}")
            evidence = retrieval.get(value, [])
            if not evidence:
                raise RuntimeError(f"fixed evidence missing for {value}")
            initial_answer = predicted_answer(initial[value])
            context = (value, query_row, evidence, initial_answer)
            contexts.append(context)
            feedback_prompts.append(feedback_prompt(tokenizer, question_text(query_row), evidence, initial_answer))
        feedback_outputs = generate_batch(model, tokenizer, feedback_prompts, decoding)
        parsed_feedback = [parse_feedback(item["text"]) for item in feedback_outputs]
        refine_prompts = [
            refinement_prompt(tokenizer, question_text(query_row), evidence, initial_answer, parsed[1], parsed[0])
            for (value, query_row, evidence, initial_answer), parsed in zip(contexts, parsed_feedback)
        ]
        refinement_outputs = generate_batch(model, tokenizer, refine_prompts, decoding)
        output_rows = []
        for context, feedback_output, parsed, refinement_output in zip(
            contexts, feedback_outputs, parsed_feedback, refinement_outputs
        ):
            value, query_row, evidence, initial_answer = context
            status, feedback_text, feedback_parse = parsed
            final_answer, refinement_parse = clean_final_answer(refinement_output["text"])
            parse_status = "ok" if feedback_parse == refinement_parse == "ok" else ";".join(
                item for item in (feedback_parse, refinement_parse) if item != "ok"
            )
            output_rows.append({
                "query_id": value,
                "dataset": dataset["label"],
                "question": question_text(query_row),
                "gold": gold_answers(query_row),
                "evidence_ids": evidence_ids(evidence),
                "selected_evidence": evidence,
                "initial_answer": initial_answer,
                "feedback_status": status,
                "feedback_text": feedback_text,
                "feedback_raw": feedback_output["text"],
                "final_answer": final_answer,
                "refinement_raw": refinement_output["text"],
                "answer_changed": final_answer.strip() != initial_answer.strip(),
                "revision_applied": final_answer.strip() != initial_answer.strip(),
                "llm_calls": 2,
                "input_tokens_feedback": feedback_output["input_tokens"],
                "output_tokens_feedback": feedback_output["output_tokens"],
                "input_tokens_refinement": refinement_output["input_tokens"],
                "output_tokens_refinement": refinement_output["output_tokens"],
                "total_input_tokens": feedback_output["input_tokens"] + refinement_output["input_tokens"],
                "total_output_tokens": feedback_output["output_tokens"] + refinement_output["output_tokens"],
                "latency_feedback_sec": feedback_output["latency_sec"],
                "latency_refinement_sec": refinement_output["latency_sec"],
                "total_latency_sec": feedback_output["latency_sec"] + refinement_output["latency_sec"],
                "latency_sec": feedback_output["latency_sec"] + refinement_output["latency_sec"],
                "parse_status": parse_status,
                "parsing_failure": parse_status != "ok",
                "model_path": str(model_path),
                "prompt_version": PROMPT_VERSION,
                "no_extra_retrieval": True,
                "fixed_retrieval_top_k": int(config["fixed_pool"]["retrieval_top_k"]),
                "generation_evidence_top_k": int(config["fixed_pool"]["generation_evidence_top_k"]),
            })
        append_jsonl(output_path, output_rows)
        completed = min(start + len(batch), len(pending))
        logger.log(f"progress={completed}/{len(pending)} appended={len(output_rows)}")
    logger.log("complete")


if __name__ == "__main__":
    main()
