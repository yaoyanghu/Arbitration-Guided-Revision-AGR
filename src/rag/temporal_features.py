from __future__ import annotations

import re
from datetime import datetime
from typing import Any


YEAR_PATTERN = re.compile(r"\b([12]?\d{3})\b")
UNCERTAINTY_MARKERS = (
    "uncertain",
    "unconfirmed",
    "rumor",
    "alleged",
    "reportedly",
    "still unsettled",
    "disputed",
)
STALE_MARKERS = (
    "former",
    "not yet",
    "previously",
    "used to",
    "earlier",
)


def extract_years(text: str) -> list[int]:
    return [int(match.group(1)) for match in YEAR_PATTERN.finditer(text)]


def _parse_time_value(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, int):
        return float(value)
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
    years = extract_years(text)
    return float(years[-1]) if years else None


def infer_query_time(query: str, explicit_query_time: str | int | None = None) -> float | None:
    if explicit_query_time is not None:
        return _parse_time_value(explicit_query_time)
    years = extract_years(query)
    return float(years[-1]) if years else None


def infer_evidence_year(candidate: dict[str, Any]) -> float | None:
    timestamp = str(candidate.get("timestamp", "")).strip()
    parsed = _parse_time_value(timestamp)
    if parsed is not None:
        return parsed
    text_years = extract_years(str(candidate.get("text", "")))
    return float(text_years[-1]) if text_years else None


def temporal_alignment_score(query: str, candidate: dict[str, Any], query_time: str | int | None = None) -> tuple[float, dict[str, Any]]:
    resolved_query_time = infer_query_time(query, query_time)
    evidence_year = infer_evidence_year(candidate)
    text = str(candidate.get("text", "")).lower()
    score = 0.0
    notes: dict[str, Any] = {
        "query_time": resolved_query_time,
        "evidence_year": evidence_year,
        "uncertainty_hits": [],
        "stale_hits": [],
    }

    if resolved_query_time is not None and evidence_year is not None:
        delta = abs(resolved_query_time - evidence_year)
        score += max(0.0, 1.0 - min(delta, 1.0))
        if delta < 0.01:
            score += 0.65
        elif evidence_year <= resolved_query_time:
            score += max(0.0, 0.55 - min(delta, 1.0) * 0.35)
        else:
            score -= 0.40 + min(delta, 1.0) * 0.40
        notes["year_gap"] = delta
    elif evidence_year is not None:
        score += 0.35
        notes["year_gap"] = None
    else:
        notes["year_gap"] = None

    uncertainty_hits = [marker for marker in UNCERTAINTY_MARKERS if marker in text]
    stale_hits = [marker for marker in STALE_MARKERS if marker in text]
    notes["uncertainty_hits"] = uncertainty_hits
    notes["stale_hits"] = stale_hits
    score -= 0.12 * len(uncertainty_hits)
    score -= 0.08 * len(stale_hits)
    return max(0.0, score), notes


def conflict_signal_score(candidate: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    text = str(candidate.get("text", "")).lower()
    support_hits = sum(text.count(token) for token in ("is", "was", "official", "confirmed", "record"))
    uncertainty_hits = sum(text.count(token) for token in ("uncertain", "unconfirmed", "disputed", "contradict"))
    score = max(0.0, min(1.0, 0.2 * support_hits - 0.15 * uncertainty_hits))
    return score, {
        "support_hits": support_hits,
        "uncertainty_hits": uncertainty_hits,
    }


def reliability_prior(candidate: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    source_type = str(candidate.get("source_type", "")).lower()
    source = str(candidate.get("source", "")).lower()
    score = 0.0

    if "official" in source_type or ".gov" in source:
        score = 1.0
    elif "knowledge_base" in source_type or "wikidata" in source:
        score = 0.65
    elif "encyclopedic" in source_type or "wikipedia" in source:
        score = 0.75
    elif "encyclopedia" in source_type:
        score = 0.70
    elif "news" in source_type:
        score = 0.55
    elif "blog" in source_type:
        score = 0.20
    elif source:
        score = 0.35

    return score, {
        "source_type": source_type,
        "source": source,
    }
