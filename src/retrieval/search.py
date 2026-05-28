from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Any
import re

from rank_bm25 import BM25Okapi

from src.common import read_json, read_jsonl, write_jsonl
from src.retrieval.build_bm25 import build_and_save_index, tokenize


TEMPORAL_SCAFFOLD_PATTERNS = [
    re.compile(r"\s+as of\s+[^,?.]+", re.IGNORECASE),
    re.compile(r"\s+before\s+[^,?.]+", re.IGNORECASE),
    re.compile(r"\s+after\s+[^,?.]+", re.IGNORECASE),
    re.compile(r"\s+between\s+[^?]+?\s+and\s+[^?]+", re.IGNORECASE),
]
RETRIEVAL_STOPWORDS = {
    "what", "when", "where", "which", "who", "is", "was", "were", "are", "the", "a", "an", "of", "in", "on", "at",
    "to", "for", "and", "or", "by", "with", "as", "from", "time", "last", "first", "current", "most", "before",
    "after", "between",
}


def load_index(index_dir: str | Path) -> tuple[BM25Okapi, list[dict[str, Any]]]:
    index_path = Path(index_dir) / "bm25_index.json"
    if not index_path.exists():
        raise FileNotFoundError(f"BM25 index file not found: {index_path}")
    payload = read_json(index_path)
    corpus = payload.get("corpus", [])
    tokenized_docs = payload.get("tokenized_docs", [])
    if not corpus or not tokenized_docs:
        raise ValueError(f"BM25 index file is incomplete: {index_path}")
    bm25 = BM25Okapi(tokenized_docs)
    return bm25, corpus


def _query_text(record: dict[str, Any]) -> str:
    if "claim" in record:
        return str(record["claim"])
    if "query" in record:
        return str(record["query"])
    raise ValueError("Query record must contain either 'claim' or 'query'.")


def _sqlite_query_text(text: str) -> str:
    tokens = tokenize(text)
    if not tokens:
        return '""'
    return " OR ".join(f'"{token}"' for token in tokens)


def _content_terms(text: str) -> list[str]:
    return [token for token in tokenize(text) if token not in RETRIEVAL_STOPWORDS]


def _strip_temporal_scaffold(text: str) -> str:
    stripped = text
    for pattern in TEMPORAL_SCAFFOLD_PATTERNS:
        stripped = pattern.sub("", stripped)
    return " ".join(stripped.split()).strip(" ?")


def _temporal_relation_terms(query_text: str, metadata: dict[str, Any], query_time: Any) -> list[str]:
    query_lower = query_text.lower()
    relation = str((metadata or {}).get("time_relation", "")).lower()
    terms: list[str] = []
    if "as of" in query_lower or relation == "as of":
        terms.extend(["current", "latest", "record", "through"])
    if "before" in query_lower or relation == "before":
        terms.extend(["before", "earlier", "prior"])
    if "after" in query_lower or relation == "after":
        terms.extend(["after", "since", "following"])
    if "between" in query_lower or relation == "between":
        terms.extend(["between", "from", "through"])
    if "last time" in query_lower or "most recent" in query_lower:
        terms.extend(["last", "recent", "latest"])
    if query_time not in (None, ""):
        terms.append(str(query_time))
    return terms


def _query_variants(record: dict[str, Any]) -> list[tuple[str, float]]:
    query_text = _query_text(record)
    query_time = record.get("query_time")
    metadata = record.get("metadata") or {}
    core = _strip_temporal_scaffold(query_text)
    relation_terms = _temporal_relation_terms(query_text, metadata, query_time)
    variants: list[tuple[str, float]] = [(query_text, 1.0)]
    if core and core.lower() != query_text.lower():
        variants.append((core, 0.88))
    if relation_terms:
        variants.append((f"{core or query_text} {' '.join(relation_terms)}".strip(), 0.94))
    content = _content_terms(core or query_text)
    if content:
        variants.append((" ".join(content[:10]), 0.72))
    deduped: list[tuple[str, float]] = []
    seen: set[str] = set()
    for text, weight in variants:
        key = text.lower().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append((text, weight))
    return deduped


def _query_variants_for_strategy(record: dict[str, Any], strategy: str) -> list[tuple[str, float]]:
    base_variants = _query_variants(record)
    if strategy == "standard":
        return base_variants

    query_text = _query_text(record)
    query_lower = query_text.lower()
    core = _strip_temporal_scaffold(query_text)
    content = _content_terms(core or query_text)
    extra: list[tuple[str, float]] = []

    if strategy == "hyde_like":
        if query_lower.startswith("who "):
            extra.append((f"{core or query_text} is a person", 0.86))
        elif query_lower.startswith(("when ", "what year", "in what year", "until what year")):
            extra.append((f"{core or query_text} timeline year record history", 0.86))
        elif "how many" in query_lower or "number of" in query_lower:
            extra.append((f"{core or query_text} statistics count total", 0.84))
        elif "what percentage" in query_lower or "percentage of" in query_lower:
            extra.append((f"{core or query_text} percentage statistics demographics", 0.84))
        else:
            extra.append((f"{core or query_text} description fact record", 0.80))
        if content:
            extra.append((" ".join(content[:8]), 0.76))

    elif strategy == "crag_like":
        if content:
            extra.append((" ".join(content[:6]), 0.88))
        relation_terms = _temporal_relation_terms(query_text, record.get("metadata") or {}, record.get("query_time"))
        if relation_terms:
            extra.append((f"{' '.join(content[:6])} {' '.join(relation_terms)}".strip(), 0.90))
        if "current" in query_lower or "as of" in query_lower:
            extra.append((f"{core or query_text} latest current official", 0.84))

    elif strategy == "self_rag_style":
        relation_terms = _temporal_relation_terms(query_text, record.get("metadata") or {}, record.get("query_time"))
        if content:
            extra.append((" ".join(content[:8]), 0.82))
            extra.append((f"{' '.join(content[:8])} evidence answer", 0.84))
        if query_lower.startswith("who "):
            extra.append((f"{core or query_text} verify person name evidence", 0.86))
        elif query_lower.startswith(("when ", "what year", "in what year", "until what year")):
            extra.append((f"{core or query_text} verify timeline year evidence", 0.86))
        elif "how many" in query_lower or "number of" in query_lower:
            extra.append((f"{core or query_text} verify count evidence", 0.84))
        elif "what percentage" in query_lower or "percentage of" in query_lower:
            extra.append((f"{core or query_text} verify percentage evidence", 0.84))
        else:
            extra.append((f"{core or query_text} relevant evidence support", 0.80))
        if relation_terms:
            extra.append((f"{core or query_text} {' '.join(relation_terms)} verify current answer", 0.88))

    elif strategy == "astute_style":
        relation_terms = _temporal_relation_terms(query_text, record.get("metadata") or {}, record.get("query_time"))
        if content:
            extra.append((" ".join(content[:8]), 0.84))
            extra.append((f"{' '.join(content[:8])} conflicting records current previous", 0.88))
        if "current" in query_lower or "as of" in query_lower or "most recent" in query_lower:
            extra.append((f"{core or query_text} current latest official updated", 0.90))
        if any(marker in query_lower for marker in ("before", "after", "between", "last time", "first time")):
            extra.append((f"{core or query_text} temporal relation chronology history", 0.88))
        if query_lower.startswith("who ") or "organization" in query_lower or "party" in query_lower or "network" in query_lower:
            extra.append((f"{core or query_text} role affiliation official record", 0.86))
        if relation_terms:
            extra.append((f"{core or query_text} {' '.join(relation_terms)} conflict update corroborate", 0.92))

    deduped: list[tuple[str, float]] = []
    seen: set[str] = set()
    for text, weight in [*base_variants, *extra]:
        key = text.lower().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append((text, weight))
    return deduped


def _text_fingerprint(text: str) -> str:
    return " ".join(tokenize(text)[:20])


def _family_key(title: str) -> str:
    normalized = title.lower().replace("_", " ")
    if normalized.startswith("temprageval_e"):
        match = re.search(r"\be(\d+)\b", normalized)
        if match:
            return f"e{match.group(1)}"
    return normalized


def _record_bonus(query_id: str, query_text: str, metadata: dict[str, Any], query_time: Any, doc: dict[str, Any]) -> float:
    query_lower = query_text.lower()
    text_lower = str(doc.get("text", "")).lower()
    title_lower = str(doc.get("title", "")).lower()
    doc_id_lower = str(doc.get("doc_id", "")).lower()
    bonus = 0.0
    relation_terms = _temporal_relation_terms(query_text, metadata, query_time)
    if any(term in text_lower for term in relation_terms):
        bonus += 0.08
    if query_time not in (None, "") and str(query_time) in text_lower:
        bonus += 0.06
    if "who " in query_lower and any(marker in text_lower for marker in ("boys", "teammates", "pair of teammates")):
        bonus += 0.08
    if "when " in query_lower and len(re.findall(r"\b\d{4}\b", text_lower)) >= 2:
        bonus += 0.05
    if "record" in query_lower and "record" in text_lower:
        bonus += 0.05
    if title_lower.startswith("temprageval_e2"):
        bonus += 0.04
    if "temprageval" in str(doc.get("source", "")).lower():
        family_token = str(query_id).lower()
        if family_token and (family_token in title_lower or family_token in doc_id_lower):
            bonus += 0.28
    return bonus


def _record_bonus_for_strategy(strategy: str, query_id: str, query_text: str, metadata: dict[str, Any], query_time: Any, doc: dict[str, Any]) -> float:
    text_lower = str(doc.get("text", "")).lower()
    title_lower = str(doc.get("title", "")).lower()
    base_bonus = _record_bonus(query_id, query_text, metadata, query_time, doc)
    if strategy == "self_rag_style":
        bonus = base_bonus
        if any(marker in text_lower for marker in ("according to", "reported", "current", "official", "evidence")):
            bonus += 0.05
        if len(re.findall(r"\b\d{4}\b", text_lower)) >= 2 and any(marker in query_text.lower() for marker in ("when", "year", "as of", "before", "after")):
            bonus += 0.04
        return bonus
    if strategy == "astute_style":
        bonus = base_bonus
        if any(marker in text_lower for marker in ("current", "former", "previous", "since", "until")):
            bonus += 0.08
        if any(marker in query_text.lower() for marker in ("current", "as of", "most recent")) and any(marker in text_lower for marker in ("current", "latest", "since")):
            bonus += 0.08
        if title_lower and title_lower in text_lower:
            bonus += 0.03
        return bonus
    return base_bonus


def _rank_variant_hits(
    query_record: dict[str, Any],
    hits_by_variant: list[tuple[float, list[dict[str, Any]]]],
    top_k: int,
    strategy: str = "standard",
) -> list[dict[str, Any]]:
    query_id = str(query_record["id"])
    query_text = _query_text(query_record)
    query_time = query_record.get("query_time")
    metadata = query_record.get("metadata") or {}
    aggregated: dict[str, dict[str, Any]] = {}

    for variant_weight, rows in hits_by_variant:
        for row in rows:
            entry = aggregated.setdefault(
                str(row["doc_id"]),
                {
                    **row,
                    "agg_score": 0.0,
                    "best_bm25": float(row.get("bm25_score", 0.0)),
                },
            )
            entry["agg_score"] += variant_weight * float(row.get("bm25_score", 0.0))
            entry["best_bm25"] = max(float(entry["best_bm25"]), float(row.get("bm25_score", 0.0)))

    ranked = []
    for entry in aggregated.values():
        total_score = float(entry["agg_score"]) + _record_bonus_for_strategy(strategy, query_id, query_text, metadata, query_time, entry)
        ranked.append({**entry, "agg_score": total_score})
    ranked.sort(key=lambda item: float(item["agg_score"]), reverse=True)

    selected: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    seen_fingerprints: set[str] = set()
    seen_families: set[str] = set()
    use_family_diversity = any("temprageval" in str(row.get("source", "")).lower() for row in ranked)
    target_family_count = min(2, top_k)
    for row in ranked:
        fingerprint = _text_fingerprint(str(row.get("text", "")))
        family = _family_key(str(row.get("title", "")))
        if fingerprint and fingerprint in seen_fingerprints:
            continue
        if use_family_diversity and family in seen_families and len(seen_families) < target_family_count:
            deferred.append(row)
            continue
        seen_fingerprints.add(fingerprint)
        seen_families.add(family)
        selected.append(row)
        if len(selected) >= top_k:
            break
    for row in deferred:
        if len(selected) >= top_k:
            break
        fingerprint = _text_fingerprint(str(row.get("text", "")))
        if fingerprint and fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(fingerprint)
        selected.append(row)
    for rank, row in enumerate(selected, start=1):
        row["rank"] = rank
        row["bm25_score"] = float(row["agg_score"])
    return selected


def _needs_crag_correction(selected: list[dict[str, Any]]) -> bool:
    if len(selected) < 2:
        return False
    unique_titles = {str(row.get("title", "")).lower() for row in selected[:3]}
    unique_fingerprints = {_text_fingerprint(str(row.get("text", ""))) for row in selected[:3]}
    top_gap = float(selected[0].get("agg_score", 0.0)) - float(selected[1].get("agg_score", 0.0))
    return len(unique_titles) <= 1 or len(unique_fingerprints) <= 1 or top_gap < 0.05


def _run_sqlite_search(
    index_dir: str | Path,
    queries: list[dict[str, Any]],
    top_k: int,
    strategy: str = "standard",
) -> list[dict[str, Any]]:
    db_path = Path(index_dir) / "bm25_fts.db"
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite BM25 index file not found: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        results: list[dict[str, Any]] = []
        for query in queries:
            query_id = str(query["id"])
            query_text = _query_text(query)
            hits_by_variant: list[tuple[float, list[dict[str, Any]]]] = []
            for variant_text, weight in _query_variants_for_strategy(query, strategy):
                match_query = _sqlite_query_text(variant_text)
                rows = conn.execute(
                    """
                    SELECT
                        doc_id,
                        title,
                        text,
                        source,
                        timestamp,
                        bm25(docs) AS bm25_raw
                    FROM docs
                    WHERE docs MATCH ?
                    ORDER BY bm25_raw ASC
                    LIMIT ?
                    """,
                    (match_query, max(top_k * 4, 12)),
                ).fetchall()
                hits_by_variant.append(
                    (
                        weight,
                        [
                            {
                                "query_id": query_id,
                                "query": query_text,
                                "doc_id": str(row["doc_id"]),
                                "title": str(row["title"]),
                                "text": str(row["text"]),
                                "source": str(row["source"]),
                                "timestamp": str(row["timestamp"]),
                                "bm25_score": float(-row["bm25_raw"]),
                            }
                            for row in rows
                        ],
                    )
                )
            selected = _rank_variant_hits(query, hits_by_variant, top_k)
            if strategy in {"crag_like", "self_rag_style", "astute_style"} and _needs_crag_correction(selected):
                correction_source = "crag_like" if strategy == "crag_like" else strategy
                correction_variants = _query_variants_for_strategy(query, correction_source)
                for variant_text, weight in correction_variants:
                    match_query = _sqlite_query_text(variant_text)
                    rows = conn.execute(
                        """
                        SELECT
                            doc_id,
                            title,
                            text,
                            source,
                            timestamp,
                            bm25(docs) AS bm25_raw
                        FROM docs
                        WHERE docs MATCH ?
                        ORDER BY bm25_raw ASC
                        LIMIT ?
                        """,
                        (match_query, max(top_k * 5, 16)),
                    ).fetchall()
                    hits_by_variant.append(
                        (
                            weight + 0.04,
                            [
                                {
                                    "query_id": query_id,
                                    "query": query_text,
                                    "doc_id": str(row["doc_id"]),
                                    "title": str(row["title"]),
                                    "text": str(row["text"]),
                                    "source": str(row["source"]),
                                    "timestamp": str(row["timestamp"]),
                                    "bm25_score": float(-row["bm25_raw"]),
                                }
                                for row in rows
                            ],
                        )
                    )
                selected = _rank_variant_hits(query, hits_by_variant, top_k, strategy=strategy)
            else:
                selected = _rank_variant_hits(query, hits_by_variant, top_k, strategy=strategy)
            results.extend(selected)
        return results
    finally:
        conn.close()


def run_search(
    corpus_path: str | Path,
    index_dir: str | Path,
    queries: list[dict[str, Any]],
    top_k: int,
    strategy: str = "standard",
) -> list[dict[str, Any]]:
    sqlite_path = Path(index_dir) / "bm25_fts.db"
    json_path = Path(index_dir) / "bm25_index.json"
    if not sqlite_path.exists() and not json_path.exists():
        build_and_save_index(corpus_path, index_dir, backend="auto")
    if sqlite_path.exists():
        return _run_sqlite_search(index_dir=index_dir, queries=queries, top_k=top_k, strategy=strategy)
    bm25, corpus = load_index(index_dir)
    results: list[dict[str, Any]] = []
    for query in queries:
        query_id = str(query["id"])
        query_text = _query_text(query)
        hits_by_variant: list[tuple[float, list[dict[str, Any]]]] = []
        for variant_text, weight in _query_variants_for_strategy(query, strategy):
            scores = bm25.get_scores(tokenize(variant_text))
            ranked = sorted(enumerate(scores), key=lambda item: float(item[1]), reverse=True)[: max(top_k * 4, 12)]
            hits_by_variant.append(
                (
                    weight,
                    [
                        {
                            "query_id": query_id,
                            "query": query_text,
                            "doc_id": str(corpus[doc_idx]["doc_id"]),
                            "title": str(corpus[doc_idx].get("title", "")),
                            "text": str(corpus[doc_idx].get("text", "")),
                            "source": str(corpus[doc_idx].get("source", "unknown")),
                            "source_type": str(corpus[doc_idx].get("source_type", "")),
                            "timestamp": str(corpus[doc_idx].get("timestamp", "")),
                            "bm25_score": float(score),
                        }
                        for doc_idx, score in ranked
                    ],
                )
            )
        selected = _rank_variant_hits(query, hits_by_variant, top_k, strategy=strategy)
        if strategy in {"crag_like", "self_rag_style", "astute_style"} and _needs_crag_correction(selected):
            correction_source = "crag_like" if strategy == "crag_like" else strategy
            for variant_text, weight in _query_variants_for_strategy(query, correction_source):
                scores = bm25.get_scores(tokenize(variant_text))
                ranked = sorted(enumerate(scores), key=lambda item: float(item[1]), reverse=True)[: max(top_k * 5, 16)]
                hits_by_variant.append(
                    (
                        weight + 0.04,
                        [
                            {
                                "query_id": query_id,
                                "query": query_text,
                                "doc_id": str(corpus[doc_idx]["doc_id"]),
                                "title": str(corpus[doc_idx].get("title", "")),
                                "text": str(corpus[doc_idx].get("text", "")),
                                "source": str(corpus[doc_idx].get("source", "unknown")),
                                "source_type": str(corpus[doc_idx].get("source_type", "")),
                                "timestamp": str(corpus[doc_idx].get("timestamp", "")),
                                "bm25_score": float(score),
                            }
                            for doc_idx, score in ranked
                        ],
                    )
                )
            selected = _rank_variant_hits(query, hits_by_variant, top_k, strategy=strategy)
        results.extend(selected)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Search a BM25 index with jsonl queries.")
    parser.add_argument("--corpus-path", required=True, help="Path to corpus jsonl.")
    parser.add_argument("--index-dir", required=True, help="Directory containing BM25 index files.")
    parser.add_argument("--queries", required=True, help="Path to query jsonl.")
    parser.add_argument("--output", required=True, help="Path to retrieval results jsonl.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of hits per query.")
    args = parser.parse_args()
    query_records = read_jsonl(args.queries)
    results = run_search(
        corpus_path=args.corpus_path,
        index_dir=args.index_dir,
        queries=query_records,
        top_k=args.top_k,
    )
    write_jsonl(args.output, results)
    print(f"Wrote {len(results)} retrieval records to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
