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
PROMPT_VERSION = "crag_fp_evaluator_v1_20260621"

EVALUATOR_SYSTEM = (
    "You are the retrieval evaluator component of a CRAG-inspired system. "
    "Assess the quality of the provided evidence for answering the question. "
    "Classify the evidence as correct, ambiguous, or incorrect. "
    "Do NOT use outside knowledge. Do NOT propose an answer."
)

EVALUATOR_INSTRUCTION = """Evaluate the quality of the fixed evidence for answering the question.

Consider:
- Does the evidence directly answer the question?
- Is the evidence relevant but incomplete?
- Is the evidence incorrect or misleading for this question?

Return exactly one compact JSON object with this schema:
{{
  "retrieval_status": "correct|ambiguous|incorrect",
  "confidence": "high|medium|low",
  "rationale": "brief explanation of the evaluation"
}}

- correct: evidence clearly supports a specific answer
- ambiguous: evidence is relevant but could support multiple answers or is incomplete
- incorrect: evidence is misleading, contradicts known facts, or is off-topic"""

REVISE_SYSTEM = (
    "You are the answer revision component of a CRAG-inspired system. "
    "Based on the retrieval evaluation, decide whether to keep or revise the initial answer. "
    "Use ONLY the fixed evidence. Do NOT introduce external knowledge."
)

REVISE_INSTRUCTION = """Revise the answer based on the retrieval evaluation.

Rules:
1. If retrieval_status is "correct" and confidence is "high", keep the initial answer unchanged.
2. If "correct" but confidence is "medium" or "low", verify and potentially refine.
3. If "ambiguous", attempt to extract the most supported answer from evidence.
4. If "incorrect", output "Insufficient evidence" (evidence is unreliable).
5. Return ONLY the shortest final answer string. No explanation."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run CRAG-inspired FP evaluator control with frozen evidence.")
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
    def replacer(match: re.Match) -> str:
        return str(lookup(config, match.group(1)))
    return pattern.sub(replacer, value)


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    return resolve_config_node(raw, raw)


def verify_frozen_inputs(root: Path, paths: list[Path]) -> None:
    for rel in paths:
        absolute = root / rel
        if not absolute.exists():
            raise FileNotFoundError(f"frozen input missing: {absolute}")


def group_retrieval(path: Path, top_k: int) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in read_jsonl(path):
        grouped[str(row["query_id"])].append(row)
    return {key: rows[:top_k] for key, rows in grouped.items()}


def prediction_map(path: Path) -> dict[str, dict[str, Any]]:
    return {str(row["query_id"]): row for row in read_jsonl(path)}


def evaluator_prompt(tokenizer: Any, question: str, evidence: list[dict[str, Any]], initial_answer: str) -> str:
    evidence_text = format_evidence(evidence)
    messages = [
        {"role": "system", "content": EVALUATOR_SYSTEM},
        {"role": "user", "content": f"Question: {question}\n\nFixed Evidence:\n{evidence_text}\n\nInitial Answer: {initial_answer}\n\n{EVALUATOR_INSTRUCTION}"},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def revise_prompt(tokenizer: Any, question: str, evidence: list[dict[str, Any]], initial_answer: str, retrieval_status: str, confidence: str, rationale: str) -> str:
    evidence_text = format_evidence(evidence)
    messages = [
        {"role": "system", "content": REVISE_SYSTEM},
        {"role": "user", "content": f"Question: {question}\n\nFixed Evidence:\n{evidence_text}\n\nInitial Answer: {initial_answer}\n\nRetrieval Status: {retrieval_status}\nConfidence: {confidence}\nRationale: {rationale}\n\n{REVISE_INSTRUCTION}"},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def generate_batch(model: Any, tokenizer: Any, prompts: list[str], decoding: dict[str, Any]) -> list[dict[str, Any]]:
    encoded = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True, max_length=3072).to(model.device)
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


def parse_evaluation(text: str) -> tuple[str, str, str, str]:
    cleaned = re.sub(r"<\\|.*?\\|>", " ", text).strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.S)
    if match:
        try:
            value = json.loads(match.group(0))
            status = str(value.get("retrieval_status", "")).strip().lower()
            confidence = str(value.get("confidence", "")).strip().lower()
            rationale = str(value.get("rationale", "")).strip()
            if status in {"correct", "ambiguous", "incorrect"} and confidence in {"high", "medium", "low"}:
                return status, confidence, rationale, "ok"
        except json.JSONDecodeError:
            pass
    fallback = " ".join(cleaned.split())[:1000] or "Evaluation output was empty; treat as ambiguous."
    return "unknown", "unknown", fallback, "evaluation_parse_fallback"


def clean_final_answer(text: str) -> tuple[str, str]:
    cleaned = re.sub(r"<\\|.*?\\|>", " ", str(text)).strip()
    cleaned = cleaned.splitlines()[0].strip() if cleaned else ""
    cleaned = re.sub(r"^(final answer|answer)\s*[:\-]\s*", "", cleaned, flags=re.I).strip(" \t\"\'\'")
    if not cleaned:
        return "Insufficient evidence", "revision_empty_fallback"
    if len(cleaned.split()) > 32:
        return " ".join(cleaned.split()[:32]), "revision_truncated"
    return cleaned, "ok"


def write_prompt_archive(output_root: Path) -> None:
    target = output_root / "prompts/crag_fp_evaluator_v1.md"
    content = (
        "# CRAG-Inspired FP Evaluator Control Prompt Archive\n\n"
        f"Prompt version: `{PROMPT_VERSION}`\n\n"
        "## Evaluator\n\n"
        f"System: {EVALUATOR_SYSTEM}\n\n"
        f"Instruction: {EVALUATOR_INSTRUCTION}\n\n"
        "## Revision\n\n"
        f"System: {REVISE_SYSTEM}\n\n"
        f"Instruction: {REVISE_INSTRUCTION}\n"
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

    default_name = f"dryrun_{args.dataset}.jsonl" if args.dry_run else f"crag_fp_evaluator_control_{args.dataset}.jsonl"
    output_path = args.output or output_root / "predictions/crag_fp_evaluator_control" / default_name
    if output_root.resolve() not in output_path.resolve().parents:
        raise RuntimeError(f"output must stay under the new adaptation root: {output_root}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = "_dryrun" if args.dry_run else ""
    logger = RunLogger(output_root / f"logs/crag_fp_evaluator_{args.dataset}{suffix}.log")

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
    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none"
    logger.log(f"model loaded cuda={torch.cuda.is_available()} gpu={gpu_name}")

    batch_size = int(decoding["batch_size"])
    for start in range(0, len(pending), batch_size):
        batch = pending[start : start + batch_size]
        contexts = []
        eval_prompts = []
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
            eval_prompts.append(evaluator_prompt(tokenizer, question_text(query_row), evidence, initial_answer))
        
        eval_outputs = generate_batch(model, tokenizer, eval_prompts, decoding)
        parsed_evals = [parse_evaluation(item["text"]) for item in eval_outputs]
        
        revise_prompts = [
            revise_prompt(tokenizer, question_text(query_row), evidence, initial_answer, parsed[0], parsed[1], parsed[2])
            for (value, query_row, evidence, initial_answer), parsed in zip(contexts, parsed_evals)
        ]
        revise_outputs = generate_batch(model, tokenizer, revise_prompts, decoding)
        
        output_rows = []
        for context, eval_output, parsed, revise_output in zip(
            contexts, eval_outputs, parsed_evals, revise_outputs
        ):
            value, query_row, evidence, initial_answer = context
            retrieval_status, confidence, rationale, eval_parse = parsed
            final_answer, revise_parse = clean_final_answer(revise_output["text"])
            parse_status = "ok" if eval_parse == revise_parse == "ok" else ";".join(
                item for item in (eval_parse, revise_parse) if item != "ok"
            )
            
            output_rows.append({
                "query_id": value,
                "dataset": dataset["label"],
                "question": question_text(query_row),
                "gold": gold_answers(query_row),
                "evidence_ids": evidence_ids(evidence),
                "selected_evidence": evidence,
                "initial_answer": initial_answer,
                "retrieval_status": retrieval_status,
                "confidence": confidence,
                "evaluation_rationale": rationale,
                "eval_raw": eval_output["text"],
                "final_answer": final_answer,
                "revise_raw": revise_output["text"],
                "answer_changed": final_answer.strip() != initial_answer.strip(),
                "revision_applied": final_answer.strip() != initial_answer.strip(),
                "llm_calls": 2,
                "input_tokens_eval": eval_output["input_tokens"],
                "output_tokens_eval": eval_output["output_tokens"],
                "input_tokens_revise": revise_output["input_tokens"],
                "output_tokens_revise": revise_output["output_tokens"],
                "total_input_tokens": eval_output["input_tokens"] + revise_output["input_tokens"],
                "total_output_tokens": eval_output["output_tokens"] + revise_output["output_tokens"],
                "latency_eval_sec": eval_output["latency_sec"],
                "latency_revise_sec": revise_output["latency_sec"],
                "total_latency_sec": eval_output["latency_sec"] + revise_output["latency_sec"],
                "latency_sec": eval_output["latency_sec"] + revise_output["latency_sec"],
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

