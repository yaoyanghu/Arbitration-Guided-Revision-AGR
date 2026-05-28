from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from src.common import ensure_dir, write_json
from src.rag.contracts import EvidenceCandidate


SLOT_TYPES = ("time", "percentage", "count", "money", "range", "role_or_entity", "generic")
CONFLICT_TYPES = ("support", "contradict", "update", "corroborate", "irrelevant")


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def feature_names() -> list[str]:
    names = [
        "bias",
        "bm25_score",
        "lexical_score",
        "temporal_score",
        "conflict_score",
        "structured_score",
        "reliability_score",
        "title_anchor_score",
    ]
    names.extend(f"slot::{slot}" for slot in SLOT_TYPES)
    names.extend(f"ctype::{ctype}" for ctype in CONFLICT_TYPES)
    return names


def feature_vector(candidate: EvidenceCandidate) -> list[float]:
    structured = candidate.notes.get("structured", {})
    slot_type = str(structured.get("slot_type", "generic"))
    conflict_type = str(structured.get("conflict_type", "corroborate"))
    values = [
        1.0,
        float(candidate.bm25_score),
        float(candidate.lexical_score),
        float(candidate.temporal_score),
        float(candidate.conflict_score),
        float(candidate.structured_score),
        float(candidate.reliability_score),
        float(candidate.notes.get("title_anchor_score", 0.0)),
    ]
    values.extend(1.0 if slot_type == slot else 0.0 for slot in SLOT_TYPES)
    values.extend(1.0 if conflict_type == ctype else 0.0 for ctype in CONFLICT_TYPES)
    return values


def train_logistic_scorer(
    rows: list[dict[str, Any]],
    *,
    epochs: int = 250,
    learning_rate: float = 0.15,
    l2: float = 1e-4,
) -> dict[str, Any]:
    names = feature_names()
    weights = [0.0 for _ in names]
    if not rows:
        return {
            "feature_names": names,
            "weights": weights,
            "epochs": 0,
            "learning_rate": learning_rate,
            "l2": l2,
            "train_rows": 0,
            "positive_rows": 0,
        }

    for _ in range(epochs):
        gradients = [0.0 for _ in weights]
        for row in rows:
            vector = row["features"]
            label = float(row["label"])
            logit = sum(weight * value for weight, value in zip(weights, vector))
            prediction = _sigmoid(logit)
            error = prediction - label
            for idx, value in enumerate(vector):
                gradients[idx] += error * value
        row_count = max(len(rows), 1)
        for idx in range(len(weights)):
            reg = l2 * weights[idx] if idx != 0 else 0.0
            weights[idx] -= learning_rate * ((gradients[idx] / row_count) + reg)

    positive_rows = sum(int(row["label"]) for row in rows)
    return {
        "feature_names": names,
        "weights": [round(weight, 8) for weight in weights],
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "train_rows": len(rows),
        "positive_rows": positive_rows,
    }


def save_scorer(model: dict[str, Any], output_path: str | Path) -> None:
    write_json(output_path, model)


def load_scorer(model_path: str | Path) -> dict[str, Any]:
    with Path(model_path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload


def score_candidate(candidate: EvidenceCandidate, model: dict[str, Any]) -> float:
    weights = [float(value) for value in model.get("weights", [])]
    vector = feature_vector(candidate)
    if len(weights) != len(vector):
        raise ValueError("Learned scorer weight dimensionality does not match feature vector.")
    return _sigmoid(sum(weight * value for weight, value in zip(weights, vector)))


def scorer_summary(model: dict[str, Any]) -> dict[str, Any]:
    names = model.get("feature_names", [])
    weights = model.get("weights", [])
    pairs = list(zip(names, weights))
    ranked = sorted(pairs, key=lambda item: abs(float(item[1])), reverse=True)
    return {
        "top_positive": [{"feature": name, "weight": weight} for name, weight in ranked if float(weight) > 0][:8],
        "top_negative": [{"feature": name, "weight": weight} for name, weight in ranked if float(weight) < 0][:8],
    }
