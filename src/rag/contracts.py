from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QueryRecord:
    query_id: str
    query: str
    answers: list[str] = field(default_factory=list)
    query_time: str | int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    gold_evidence_titles: list[str] = field(default_factory=list)
    gold_evidence_texts: list[str] = field(default_factory=list)


@dataclass
class EvidenceRecord:
    doc_id: str
    title: str
    text: str
    source: str = ""
    source_type: str = ""
    timestamp: str = ""
    url: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceCandidate:
    query_id: str
    query: str
    doc_id: str
    title: str
    text: str
    source: str
    source_type: str
    timestamp: str
    bm25_score: float
    lexical_score: float = 0.0
    temporal_score: float = 0.0
    conflict_score: float = 0.0
    structured_score: float = 0.0
    learned_score: float = 0.0
    reliability_score: float = 0.0
    arbitration_score: float = 0.0
    citation_id: str = ""
    notes: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnswerPrediction:
    query_id: str
    query: str
    predicted_answer: str
    selected_evidence: list[dict[str, Any]]
    arbitration_trace: dict[str, Any]
    metrics: dict[str, Any] = field(default_factory=dict)


def _extract_answers(record: dict[str, Any]) -> list[str]:
    for key in ("answers", "answer", "gold_answers"):
        value = record.get(key)
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
    if "label" in record:
        return [str(record["label"]).strip()]
    return []


def to_query_record(record: dict[str, Any]) -> QueryRecord:
    query = str(record.get("query") or record.get("claim") or "").strip()
    if not query:
        raise ValueError("Query record must contain `query` or `claim`.")
    metadata = {
        "dataset": str(record.get("source_dataset") or record.get("source") or ""),
        "split": str(record.get("split") or ""),
        "query_type": str(record.get("query_type") or record.get("case_type") or ""),
    }
    query_time = record.get("query_time")
    if query_time is not None:
        try:
            query_time = int(query_time)
        except (TypeError, ValueError):
            query_time = str(query_time).strip() or None
    return QueryRecord(
        query_id=str(record["id"]),
        query=query,
        answers=_extract_answers(record),
        query_time=query_time,
        metadata=metadata,
        gold_evidence_titles=[
            str(item).strip()
            for item in (record.get("gold_evidence_titles") or record.get("evidence_titles") or [])
            if str(item).strip()
        ],
        gold_evidence_texts=[
            str(item).strip()
            for item in (record.get("gold_evidence_texts") or record.get("evidence") or [])
            if str(item).strip()
        ],
    )


def to_evidence_candidate(record: dict[str, Any]) -> EvidenceCandidate:
    return EvidenceCandidate(
        query_id=str(record["query_id"]),
        query=str(record.get("query", "")),
        doc_id=str(record.get("doc_id", "")),
        title=str(record.get("title", "")),
        text=str(record.get("text", "")),
        source=str(record.get("source", "")),
        source_type=str(record.get("source_type", "")),
        timestamp=str(record.get("timestamp", "")),
        bm25_score=float(record.get("bm25_score", 0.0)),
        notes={},
    )
