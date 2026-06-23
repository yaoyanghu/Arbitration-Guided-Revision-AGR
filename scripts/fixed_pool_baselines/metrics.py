from __future__ import annotations

import random
from collections import Counter
from typing import Any, Callable

# Canonical project metric definitions. Do not replace with a second normalization.
# Source: src/eval/eval_conflict_aware_rag.py::{_normalize_text, exact_match, token_f1}
from src.eval.eval_conflict_aware_rag import _normalize_text, exact_match, token_f1


def precision_recall(prediction: str, gold_answers: list[str]) -> tuple[float, float]:
    pred_tokens = _normalize_text(prediction).split()
    if not gold_answers:
        return 0.0, 0.0
    best_precision, best_recall, best_f1 = 0.0, 0.0, -1.0
    for answer in gold_answers:
        gold_tokens = _normalize_text(answer).split()
        if not pred_tokens and not gold_tokens:
            candidate = (1.0, 1.0, 1.0)
        elif not pred_tokens or not gold_tokens:
            candidate = (0.0, 0.0, 0.0)
        else:
            common = sum((Counter(pred_tokens) & Counter(gold_tokens)).values())
            precision = common / len(pred_tokens)
            recall = common / len(gold_tokens)
            f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
            candidate = (precision, recall, f1)
        if candidate[2] > best_f1:
            best_precision, best_recall, best_f1 = candidate
    return best_precision, best_recall


def metric_payload(prediction: str, answers: list[str]) -> dict[str, float]:
    precision, recall = precision_recall(prediction, answers)
    return {
        "EM": exact_match(prediction, answers),
        "F1": token_f1(prediction, answers),
        "Precision": precision,
        "Recall": recall,
    }


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def percentile(sorted_values: list[float], proportion: float) -> float:
    if not sorted_values:
        return 0.0
    index = max(0, min(len(sorted_values) - 1, int(proportion * len(sorted_values))))
    return sorted_values[index]


def bootstrap_mean_ci(
    values: list[float], resamples: int = 10000, seed: int = 42
) -> tuple[float, float, float]:
    observed = mean(values)
    if not values:
        return observed, 0.0, 0.0
    rng = random.Random(seed)
    n = len(values)
    samples = [mean([values[rng.randrange(n)] for _ in range(n)]) for _ in range(resamples)]
    samples.sort()
    return observed, percentile(samples, 0.025), percentile(samples, 0.975)


def recorded_token_counts(row: dict[str, Any]) -> tuple[int | None, int | None]:
    input_keys = ("total_input_tokens", "input_tokens", "input_token_count")
    output_keys = ("total_output_tokens", "output_tokens", "generation_token_count")
    input_count = next((int(row[key]) for key in input_keys if row.get(key) not in (None, "", "NA", "not_logged")), None)
    output_count = next((int(row[key]) for key in output_keys if row.get(key) not in (None, "", "NA", "not_logged")), None)
    return input_count, output_count


def bootstrap_rows(
    per_query: list[dict[str, Any]],
    baseline_present: bool,
    resamples: int,
    seed: int,
) -> list[dict[str, Any]]:
    import numpy as np

    metrics = [f"delta_{metric}" if baseline_present else metric for metric in ("EM", "F1", "Precision", "Recall")]
    matrix = np.asarray([[float(row[key]) for key in metrics] for row in per_query], dtype=np.float64)
    rng = np.random.default_rng(seed)
    bootstrap_values = np.empty((resamples, len(metrics)), dtype=np.float64)
    n = len(per_query)
    if n:
        for start in range(0, resamples, 256):
            stop = min(start + 256, resamples)
            indices = rng.integers(0, n, size=(stop - start, n))
            bootstrap_values[start:stop] = matrix[indices].mean(axis=1)
    else:
        bootstrap_values.fill(0.0)
    rows: list[dict[str, Any]] = []
    for index, key in enumerate(metrics):
        values = matrix[:, index] if n else np.asarray([], dtype=np.float64)
        observed = float(values.mean()) if n else 0.0
        low = float(np.quantile(bootstrap_values[:, index], 0.025))
        high = float(np.quantile(bootstrap_values[:, index], 0.975))
        rows.append({
            "metric": key,
            "observed": observed,
            "ci_low": low,
            "ci_high": high,
            "bootstrap_resamples": resamples,
            "seed": seed,
            "paired_by": "query_id",
            "n": len(values),
        })
    return rows
