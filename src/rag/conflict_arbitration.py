from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from math import exp
from typing import Any
import re

from src.rag.contracts import EvidenceCandidate, QueryRecord, to_evidence_candidate
from src.rag.learned_scorer import score_candidate
from src.rag.structured_arbitration import compute_structured_signal
from src.rag.temporal_features import conflict_signal_score, reliability_prior, temporal_alignment_score

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")
STOPWORDS = {
    "what", "when", "where", "which", "who", "whom", "why", "how", "is", "was", "were", "are", "the", "a", "an",
    "of", "in", "on", "at", "to", "for", "and", "or", "by", "with", "as", "from", "before", "after", "between",
    "time", "last", "first", "percentage", "name", "compared", "nationally",
}

VALUE_PATTERN = re.compile(
    r"\$[\d,]+(?:\.\d+)?|\d+(?:\.\d+)?%|\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\b([12]?\d{3})\b"
)


def _content_tokens(text: str) -> set[str]:
    return {token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOPWORDS and len(token) > 2}


def _title_anchor_score(query_record: QueryRecord, candidate: EvidenceCandidate) -> float:
    query_tokens = _content_tokens(query_record.query)
    title_tokens = _content_tokens(candidate.title)
    if not query_tokens or not title_tokens:
        return 0.0
    return len(query_tokens & title_tokens) / max(len(title_tokens), 1)


def _parse_time_value(value: str) -> float | None:
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            dt = datetime.strptime(text, fmt)
            year_start = datetime(dt.year, 1, 1)
            next_year_start = datetime(dt.year + 1, 1, 1)
            return dt.year + (dt - year_start).total_seconds() / max((next_year_start - year_start).total_seconds(), 1.0)
        except ValueError:
            continue
    match = re.search(r"\b([12]?\d{3})\b", text)
    return float(match.group(1)) if match else None


def _primary_value_signature(text: str) -> str:
    text_lower = text.lower()
    compared_match = re.search(
        r"(\$[\d,]+(?:\.\d+)?|\d+(?:\.\d+)?%?)\s*,?\s*compared with\s*(\$[\d,]+(?:\.\d+)?|\d+(?:\.\d+)?%?)\s+nationally",
        text_lower,
    )
    if compared_match:
        return f"cmp:{compared_match.group(1)}|{compared_match.group(2)}"
    range_match = re.search(r"\b(\d{4}\s*(?:-|to|[^A-Za-z0-9\s]{1,4})\s*\d{2,4})\b", text_lower)
    if range_match:
        return f"range:{range_match.group(1)}"
    value_match = VALUE_PATTERN.search(text)
    if value_match:
        return f"val:{value_match.group(0)}"
    quote_match = re.search(r"\"([^\"]+)\"", text)
    if quote_match:
        return f"quote:{quote_match.group(1).strip().lower()}"
    return ""


def _apply_pairwise_conflict_arbitration(candidates: list[EvidenceCandidate]) -> None:
    grouped: dict[tuple[str, str], list[EvidenceCandidate]] = defaultdict(list)
    for candidate in candidates:
        grouped[(candidate.query_id, candidate.title.strip().lower())].append(candidate)

    for items in grouped.values():
        if len(items) < 2:
            continue
        signatures = {_primary_value_signature(item.text) for item in items if _primary_value_signature(item.text)}
        if len(signatures) < 2:
            continue

        timed_items = [(item, _parse_time_value(item.timestamp)) for item in items]
        known_times = [value for _, value in timed_items if value is not None]
        if not known_times:
            continue
        freshest = max(known_times)
        stalest = min(known_times)

        for item, time_value in timed_items:
            bonus = 0.0
            if time_value is not None:
                if abs(time_value - freshest) < 1e-6:
                    bonus += 0.55
                elif abs(time_value - stalest) < 1e-6:
                    bonus -= 0.20
                else:
                    bonus += 0.10
            if "current " in item.text.lower() or " current" in item.text.lower():
                bonus += 0.10
            item.conflict_score = max(0.0, min(1.0, item.conflict_score + bonus))
            item.notes["conflict"]["pairwise_signature"] = _primary_value_signature(item.text)
            item.notes["conflict"]["pairwise_bonus"] = round(bonus, 4)


def _softmax(values: list[float]) -> list[float]:
    if not values:
        return []
    pivot = max(values)
    exps = [exp(value - pivot) for value in values]
    total = sum(exps)
    if total <= 0:
        return [1.0 / len(values)] * len(values)
    return [value / total for value in exps]


def _symbolic_query_gate(query_record: QueryRecord, candidates: list[EvidenceCandidate], fixed_gamma: float, gate_enabled: bool) -> tuple[float, dict[str, Any]]:
    if not gate_enabled:
        gamma = max(0.0, min(1.0, fixed_gamma))
        return gamma, {
            "gate_enabled": False,
            "explicit_temporal_operator": 0.0,
            "candidate_year_dispersion": 0.0,
            "same_title_conflict_density": 0.0,
            "candidate_span_type_confidence": 0.0,
        }

    query_lower = query_record.query.lower()
    explicit_temporal_operator = 1.0 if any(
        marker in query_lower for marker in ("as of", "before", "after", "between", "current", "most recent", "latest", "first time", "last time")
    ) else 0.0

    years = [value for value in (_parse_time_value(item.timestamp) for item in candidates) if value is not None]
    if len(years) >= 2:
        year_span = max(years) - min(years)
        candidate_year_dispersion = max(0.0, min(1.0, year_span / 10.0))
    else:
        candidate_year_dispersion = 0.0

    grouped: dict[str, list[EvidenceCandidate]] = defaultdict(list)
    for item in candidates:
        grouped[item.title.strip().lower()].append(item)
    conflict_groups = 0
    for items in grouped.values():
        signatures = {_primary_value_signature(item.text) for item in items if _primary_value_signature(item.text)}
        if len(signatures) >= 2:
            conflict_groups += 1
    same_title_conflict_density = conflict_groups / max(len(grouped), 1)

    candidate_span_type_confidence = 0.0
    if candidates:
        candidate_span_type_confidence = sum(item.structured_score for item in candidates[: min(3, len(candidates))]) / min(3, len(candidates))

    gamma = (
        0.15
        + 0.35 * explicit_temporal_operator
        + 0.25 * candidate_year_dispersion
        + 0.15 * same_title_conflict_density
        + 0.10 * candidate_span_type_confidence
    )
    gamma = max(0.05, min(0.95, gamma))
    return gamma, {
        "gate_enabled": True,
        "explicit_temporal_operator": round(explicit_temporal_operator, 4),
        "candidate_year_dispersion": round(candidate_year_dispersion, 4),
        "same_title_conflict_density": round(same_title_conflict_density, 4),
        "candidate_span_type_confidence": round(candidate_span_type_confidence, 4),
    }


def _normalize_by_query(candidates: list[EvidenceCandidate], field: str) -> None:
    grouped: dict[str, list[EvidenceCandidate]] = defaultdict(list)
    for candidate in candidates:
        grouped[candidate.query_id].append(candidate)
    for items in grouped.values():
        values = [float(getattr(item, field)) for item in items]
        min_value = min(values)
        max_value = max(values)
        for item in items:
            raw = float(getattr(item, field))
            if max_value == min_value:
                normalized = 1.0 if raw > 0 else 0.0
            else:
                normalized = (raw - min_value) / (max_value - min_value)
            setattr(item, field, normalized)


def build_scored_candidates(
    query_records: list[QueryRecord],
    retrieval_records: list[dict[str, Any]],
    bm25_weight: float,
    lexical_weight: float,
    temporal_weight: float,
    conflict_weight: float,
    structured_weight: float,
    reliability_weight: float,
    learned_weight: float = 0.0,
    learned_model: dict[str, Any] | None = None,
    posterior_enabled: bool = False,
    gate_enabled: bool = False,
    fixed_gamma: float = 0.5,
    family_conflict_weight: float = 0.7,
    global_conflict_weight: float = 0.3,
) -> list[EvidenceCandidate]:
    query_lookup = {record.query_id: record for record in query_records}
    candidates = [to_evidence_candidate(record) for record in retrieval_records]
    _normalize_by_query(candidates, "bm25_score")

    for candidate in candidates:
        query_record = query_lookup[candidate.query_id]
        query_tokens = _content_tokens(query_record.query)
        evidence_tokens = _content_tokens(candidate.title + " " + candidate.text)
        lexical_overlap = len(query_tokens & evidence_tokens) / max(len(query_tokens), 1)
        title_anchor = _title_anchor_score(query_record, candidate)
        candidate.lexical_score = 0.65 * lexical_overlap + 0.35 * title_anchor
        candidate.temporal_score, temporal_notes = temporal_alignment_score(
            query_record.query,
            candidate.__dict__,
            query_record.query_time,
        )
        candidate.conflict_score, conflict_notes = conflict_signal_score(candidate.__dict__)
        candidate.structured_score, structured_notes = compute_structured_signal(query_record, candidate)
        candidate.reliability_score, reliability_notes = reliability_prior(candidate.__dict__)
        candidate.learned_score = score_candidate(candidate, learned_model) if learned_model else 0.0
        candidate.retrieval_prior = (
            bm25_weight * candidate.bm25_score
            + lexical_weight * candidate.lexical_score
        )
        candidate.temporal_expert_score = temporal_weight * candidate.temporal_score
        candidate.conflict_expert_score = (
            conflict_weight * candidate.conflict_score
            + structured_weight * candidate.structured_score
            + reliability_weight * candidate.reliability_score
            + learned_weight * candidate.learned_score
        )
        candidate.notes = {
            "temporal": temporal_notes,
            "conflict": conflict_notes,
            "structured": structured_notes,
            "reliability": reliability_notes,
            "title_anchor_score": title_anchor,
        }
        candidate.evidence_logit = (
            candidate.retrieval_prior
            + candidate.temporal_expert_score
            + candidate.conflict_expert_score
        )
        candidate.arbitration_score = candidate.evidence_logit

    _apply_pairwise_conflict_arbitration(candidates)
    grouped: dict[str, list[EvidenceCandidate]] = defaultdict(list)
    for candidate in candidates:
        candidate.conflict_expert_score = (
            conflict_weight * candidate.conflict_score
            + structured_weight * candidate.structured_score
            + reliability_weight * candidate.reliability_score
            + learned_weight * candidate.learned_score
        )
        candidate.evidence_logit = (
            candidate.retrieval_prior
            + candidate.temporal_expert_score
            + candidate.conflict_expert_score
        )
        grouped[candidate.query_id].append(candidate)

    for query_id, items in grouped.items():
        query_record = query_lookup[query_id]
        gamma, gate_trace = _symbolic_query_gate(query_record, items, fixed_gamma=fixed_gamma, gate_enabled=gate_enabled if posterior_enabled else False)
        logits = [item.evidence_logit for item in items]
        weights = _softmax(logits)
        rounded_weights = [round(weight, 4) for weight in weights]
        global_conflict = sum(weight * item.conflict_expert_score for weight, item in zip(weights, items))
        by_title: dict[str, float] = defaultdict(float)
        for weight, item in zip(weights, items):
            by_title[item.title.strip().lower()] += weight * item.conflict_expert_score

        for item, attention_weight in zip(items, weights):
            item.evidence_attention_weight = attention_weight
            item.gate_gamma = gamma
            family_conflict = by_title[item.title.strip().lower()]
            if posterior_enabled:
                family_w = max(0.0, float(family_conflict_weight))
                global_w = max(0.0, float(global_conflict_weight))
                norm = family_w + global_w
                if norm <= 0.0:
                    family_w, global_w = 0.7, 0.3
                    norm = 1.0
                family_w /= norm
                global_w /= norm
                item.arbitration_score = (
                    item.retrieval_prior
                    + gamma * item.temporal_expert_score
                    + (1.0 - gamma) * (family_w * family_conflict + global_w * global_conflict)
                )
            else:
                item.arbitration_score = (
                    item.retrieval_prior
                    + item.temporal_expert_score
                    + item.conflict_expert_score
                )
            item.notes["posterior"] = {
                "posterior_enabled": posterior_enabled,
                "retrieval_prior": round(item.retrieval_prior, 4),
                "temporal_expert_score": round(item.temporal_expert_score, 4),
                "conflict_expert_score": round(item.conflict_expert_score, 4),
                "evidence_logit": round(item.evidence_logit, 4),
                "evidence_attention_weight": round(item.evidence_attention_weight, 4),
                "evidence_attention_weights": rounded_weights,
                "gate_gamma": round(item.gate_gamma, 4),
                **gate_trace,
            }

    return sorted(candidates, key=lambda item: (item.query_id, -item.arbitration_score, -item.bm25_score))


def select_evidence_bundle(
    candidates: list[EvidenceCandidate],
    evidence_top_k: int,
    enable_top_gap_filtering: bool = True,
    enable_duplicate_suppression: bool = True,
    top_gap_threshold: float = 0.10,
) -> dict[str, list[EvidenceCandidate]]:
    grouped: dict[str, list[EvidenceCandidate]] = defaultdict(list)
    for candidate in candidates:
        grouped[candidate.query_id].append(candidate)
    bundles: dict[str, list[EvidenceCandidate]] = {}
    for query_id, items in grouped.items():
        ranked = sorted(items, key=lambda item: item.arbitration_score, reverse=True)
        selected = []
        seen_doc_ids: set[str] = set()
        if ranked and enable_top_gap_filtering:
            top_gap = ranked[0].arbitration_score - (ranked[1].arbitration_score if len(ranked) > 1 else 0.0)
            strong_top1 = ranked[0].lexical_score >= 0.45 or float(ranked[0].notes.get("title_anchor_score", 0.0)) >= 0.45
            if top_gap >= float(top_gap_threshold) and strong_top1:
                ranked = ranked[:1]
        for item in ranked:
            if enable_duplicate_suppression and item.doc_id in seen_doc_ids:
                continue
            if selected:
                same_title = item.title.strip().lower() == selected[0].title.strip().lower()
                if not same_title and item.arbitration_score < selected[0].arbitration_score - 0.05:
                    continue
            seen_doc_ids.add(item.doc_id)
            selected.append(item)
            if len(selected) >= evidence_top_k:
                break
        for index, item in enumerate(selected, start=1):
            item.citation_id = f"[{index}]"
        bundles[query_id] = selected
    return bundles
