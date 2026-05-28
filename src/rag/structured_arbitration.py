from __future__ import annotations

import re
from typing import Any

from src.rag.contracts import EvidenceCandidate, QueryRecord


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9%$'-]+")
YEAR_PATTERN = re.compile(r"\b((?:18|19|20|21)\d{2})\b")
PERCENT_PATTERN = re.compile(r"\b\d+(?:\.\d+)?%")
MONEY_PATTERN = re.compile(r"\$[\d,]+(?:\.\d+)?")
COUNT_PATTERN = re.compile(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\b\d+\b")
RANGE_PATTERN = re.compile(r"\b((?:18|19|20|21)\d{2}\s*(?:-|to)\s*(?:\d{2,4}))\b", re.IGNORECASE)
CAPITALIZED_NAME_PATTERN = re.compile(r"\b[A-Z][A-Za-z'&.-]+(?:\s+[A-Z][A-Za-z'&.-]+){0,5}\b")
SUPPORT_CUES = ("is", "was", "are", "were", "current", "served as", "holds", "has")
UPDATE_CUES = ("current", "as of", "latest", "most recent", "now", "since")
CONTRADICT_CUES = ("former", "previously", "ex-", "no longer", "until", "before")
IRRELEVANT_CUES = ("history", "background", "founded", "located", "born")
STOPWORDS = {
    "what", "when", "where", "which", "who", "whom", "why", "how", "is", "was", "were", "are", "the", "a", "an",
    "of", "in", "on", "at", "to", "for", "and", "or", "by", "with", "as", "from", "before", "after", "between",
    "current", "name", "number", "many", "much", "percentage", "percent", "value", "year",
}


def _tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def _content_tokens(text: str) -> set[str]:
    return {token for token in _tokenize(text) if token not in STOPWORDS and len(token) > 2}


def _query_slot(question: str) -> str:
    q = question.lower()
    if q.startswith(("when", "what year", "in what year")) or " as of " in q or " before " in q or " after " in q:
        return "time"
    if "what percentage" in q or "percentage of" in q:
        return "percentage"
    if q.startswith("how many") or "number of" in q or "count of" in q:
        return "count"
    if "median income" in q or "salary" in q or "budget" in q or "revenue" in q:
        return "money"
    if q.startswith("who ") or "affiliation" in q or "organization" in q or "party" in q or "network" in q or "president" in q:
        return "role_or_entity"
    if "time period" in q or "range" in q:
        return "range"
    return "generic"


def _extract_value_signatures(text: str, slot_type: str) -> list[str]:
    if slot_type == "time":
        return [match.group(1) for match in YEAR_PATTERN.finditer(text)]
    if slot_type == "percentage":
        return [match.group(0) for match in PERCENT_PATTERN.finditer(text)]
    if slot_type == "money":
        return [match.group(0) for match in MONEY_PATTERN.finditer(text)]
    if slot_type == "count":
        values = [match.group(0) for match in COUNT_PATTERN.finditer(text)]
        return [value for value in values if "%" not in value and not value.startswith("$")]
    if slot_type == "range":
        return [match.group(1) for match in RANGE_PATTERN.finditer(text)]
    if slot_type == "role_or_entity":
        return [match.group(0).strip() for match in CAPITALIZED_NAME_PATTERN.finditer(text)]
    return []


def _query_entity_tokens(question: str) -> set[str]:
    return _content_tokens(question)


def _candidate_entity_score(query_tokens: set[str], candidate: EvidenceCandidate) -> float:
    title_tokens = _content_tokens(candidate.title)
    text_tokens = _content_tokens(candidate.text)
    if not query_tokens:
        return 0.0
    title_overlap = len(query_tokens & title_tokens) / max(len(query_tokens), 1)
    text_overlap = len(query_tokens & text_tokens) / max(len(query_tokens), 1)
    return 0.65 * title_overlap + 0.35 * text_overlap


def _slot_value_match_score(slot_type: str, candidate: EvidenceCandidate) -> tuple[float, list[str]]:
    notes: list[str] = []
    text = candidate.text
    signatures = _extract_value_signatures(text, slot_type)
    if not signatures:
        if slot_type in {"time", "percentage", "count", "money", "range"}:
            notes.append("missing_expected_value_type")
            return -0.18, notes
        return 0.0, notes

    if slot_type == "role_or_entity":
        title_like = candidate.title.strip().lower() in text.strip().lower()
        if title_like and len(signatures) <= 1:
            notes.append("title_like_role_span_risk")
            return -0.08, notes
        notes.append("entity_like_value_present")
        return 0.18, notes

    if len(signatures) > 1 and slot_type in {"count", "percentage", "money"}:
        notes.append("same_format_multiple_values")
        return 0.05, notes

    notes.append("slot_value_present")
    return 0.18, notes


def _freshness_consistency_score(query_record: QueryRecord, candidate: EvidenceCandidate) -> tuple[float, list[str]]:
    q = query_record.query.lower()
    text = candidate.text.lower()
    notes: list[str] = []
    score = 0.0
    if any(marker in q for marker in ("current", "as of", "latest", "most recent", "now")):
        if any(marker in text for marker in UPDATE_CUES):
            score += 0.16
            notes.append("freshness_cue_match")
        if any(marker in text for marker in CONTRADICT_CUES):
            score -= 0.08
            notes.append("stale_cue_penalty")
    if any(marker in q for marker in ("before", "until", "formerly", "previous")) and any(marker in text for marker in CONTRADICT_CUES):
        score += 0.10
        notes.append("historical_cue_match")
    return score, notes


def _conflict_type(query_record: QueryRecord, candidate: EvidenceCandidate) -> str:
    q = query_record.query.lower()
    text = candidate.text.lower()
    if any(marker in q for marker in ("current", "as of", "latest", "most recent")) and any(marker in text for marker in UPDATE_CUES):
        return "update"
    if any(marker in text for marker in CONTRADICT_CUES):
        return "contradict"
    if any(marker in text for marker in IRRELEVANT_CUES) and not any(marker in text for marker in SUPPORT_CUES):
        return "irrelevant"
    if any(marker in text for marker in SUPPORT_CUES):
        return "support"
    return "corroborate"


def compute_structured_signal(query_record: QueryRecord, candidate: EvidenceCandidate) -> tuple[float, dict[str, Any]]:
    slot_type = _query_slot(query_record.query)
    query_tokens = _query_entity_tokens(query_record.query)

    entity_score = _candidate_entity_score(query_tokens, candidate)
    slot_score, slot_notes = _slot_value_match_score(slot_type, candidate)
    freshness_score, freshness_notes = _freshness_consistency_score(query_record, candidate)

    same_title_penalty = 0.0
    if slot_type == "role_or_entity":
        candidate_title_tokens = _content_tokens(candidate.title)
        if candidate_title_tokens and candidate_title_tokens <= query_tokens:
            same_title_penalty = -0.10

    conflict_type = _conflict_type(query_record, candidate)
    conflict_bonus = {
        "support": 0.08,
        "update": 0.12,
        "corroborate": 0.04,
        "contradict": -0.10,
        "irrelevant": -0.16,
    }[conflict_type]

    score = entity_score * 0.45 + slot_score + freshness_score + same_title_penalty + conflict_bonus
    score = max(0.0, min(1.0, 0.5 + score))

    notes = {
        "slot_type": slot_type,
        "entity_score": round(entity_score, 4),
        "slot_notes": slot_notes,
        "freshness_notes": freshness_notes,
        "same_title_penalty": round(same_title_penalty, 4),
        "conflict_type": conflict_type,
        "value_signatures": _extract_value_signatures(candidate.text, slot_type)[:5],
    }
    return score, notes
