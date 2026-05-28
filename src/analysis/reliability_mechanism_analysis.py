from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_json, read_jsonl, write_json, write_jsonl
from src.rerank.rerank import score_and_rank_records

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "had",
    "has",
    "have",
    "in",
    "is",
    "it",
    "its",
    "no",
    "not",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "to",
    "was",
    "were",
    "with",
}

RELATION_LABELS = ["support", "complement", "granularity_mismatch", "conflict"]
FAILURE_REASON_LABELS = [
    "bm25_already_correct",
    "reliability_changed_non-gold_items_only",
    "source_score_direction_wrong",
    "source_difference_not_relevant_to_query",
    "supporting_source_has_less_lexical_match",
]

ATTRIBUTE_HINTS = (
    " is ",
    " was ",
    " are ",
    " were ",
    " has ",
    " had ",
    " born ",
    " died ",
    " premiered ",
    " released ",
    " started ",
    " began ",
    " married ",
    " population ",
    " capital ",
    " president ",
    " governor ",
    " mayor ",
    " located ",
    " from ",
)


def normalize_source(source: str) -> str:
    text = source.lower()
    if "wikidata" in text:
        return "wikidata"
    if "wikipedia" in text:
        return "wikipedia"
    return text or "unknown"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text.lower())


def content_tokens(text: str) -> set[str]:
    return {token for token in tokenize(text) if token not in STOPWORDS}


def extract_numbers(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:\.\d+)?\b", text))


def lexical_overlap(query_text: str, doc_text: str) -> float:
    query_tokens = content_tokens(query_text)
    if not query_tokens:
        return 0.0
    doc_tokens = content_tokens(doc_text)
    return len(query_tokens & doc_tokens) / len(query_tokens)


def classify_query_type(claim: str) -> str:
    lowered = f" {claim.lower()} "
    token_count = len(content_tokens(claim))
    has_attribute_hint = any(hint in lowered for hint in ATTRIBUTE_HINTS)
    has_number = bool(extract_numbers(claim))
    if has_attribute_hint and (token_count <= 16 or has_number):
        return "attribute"
    return "descriptive"


def relation_label(claim: str, wiki_text: str, wikidata_text: str) -> str:
    claim_tokens = content_tokens(claim)
    wiki_overlap = lexical_overlap(claim, wiki_text)
    wikidata_overlap = lexical_overlap(claim, wikidata_text)
    claim_numbers = extract_numbers(claim)
    wiki_numbers = extract_numbers(wiki_text)
    wikidata_numbers = extract_numbers(wikidata_text)

    if claim_numbers:
        wiki_match = bool(claim_numbers & wiki_numbers)
        wikidata_match = bool(claim_numbers & wikidata_numbers)
        wiki_conflict = bool(wiki_numbers) and not wiki_match
        wikidata_conflict = bool(wikidata_numbers) and not wikidata_match
        if wiki_match != wikidata_match and (wiki_conflict or wikidata_conflict):
            return "conflict"

    if wiki_overlap >= 0.45 and wikidata_overlap >= 0.45:
        return "support"

    if len(content_tokens(wiki_text)) >= max(2 * len(content_tokens(wikidata_text)), 12):
        if wiki_overlap > wikidata_overlap:
            return "granularity_mismatch"

    if (claim_tokens & content_tokens(wiki_text)) and (claim_tokens & content_tokens(wikidata_text)):
        return "complement"

    return "granularity_mismatch"


def gold_closer_source(claim: str, wiki_text: str, wikidata_text: str) -> str:
    wiki_overlap = lexical_overlap(claim, wiki_text)
    wikidata_overlap = lexical_overlap(claim, wikidata_text)
    if abs(wiki_overlap - wikidata_overlap) < 0.05:
        return "both"
    return "wikipedia" if wiki_overlap > wikidata_overlap else "wikidata"


def base_reliability_score(source: str) -> float:
    normalized = normalize_source(source)
    if normalized == "wikipedia":
        return 1.0
    if normalized == "wikidata":
        return 0.85
    return 0.5


def query_aware_reliability_score(source: str, query_type: str) -> float:
    normalized = normalize_source(source)
    if query_type == "attribute":
        if normalized == "wikidata":
            return 1.1
        if normalized == "wikipedia":
            return 0.9
    if normalized == "wikipedia":
        return 1.0
    if normalized == "wikidata":
        return 0.85
    return 0.5


def group_by_query(records: list[dict[str, Any]], rank_field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["query_id"])].append(record)
    for query_id, items in grouped.items():
        grouped[query_id] = sorted(items, key=lambda item: int(item.get(rank_field, 10**9)))
    return dict(grouped)


def best_rank_for_source(records: list[dict[str, Any]], source_name: str, rank_field: str) -> int | None:
    ranks = [
        int(record.get(rank_field, 10**9))
        for record in records
        if normalize_source(str(record.get("source_name") or record.get("source", ""))) == source_name
    ]
    return min(ranks) if ranks else None


def best_record_for_source(records: list[dict[str, Any]], source_name: str, rank_field: str) -> dict[str, Any] | None:
    candidates = [
        record
        for record in records
        if normalize_source(str(record.get("source_name") or record.get("source", ""))) == source_name
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: int(item.get(rank_field, 10**9)))[0]


def source_order_signature(records: list[dict[str, Any]], rank_field: str) -> tuple[str, str]:
    wiki_rank = best_rank_for_source(records, "wikipedia", rank_field)
    wikidata_rank = best_rank_for_source(records, "wikidata", rank_field)
    if wiki_rank is None or wikidata_rank is None:
        return ("unknown", "unknown")
    preferred = "wikipedia" if wiki_rank < wikidata_rank else "wikidata"
    alternate = "wikidata" if preferred == "wikipedia" else "wikipedia"
    return (preferred, alternate)


def build_query_aware_records(
    records: list[dict[str, Any]],
    query_type_map: dict[str, str],
    bm25_weight: float,
    temporal_weight: float,
    reliability_weight: float,
) -> list[dict[str, Any]]:
    query_aware_records: list[dict[str, Any]] = []
    for record in records:
        query_id = str(record["query_id"])
        query_type = query_type_map[query_id]
        enriched = dict(record)
        enriched["reliability_score"] = query_aware_reliability_score(
            str(record.get("source_name") or record.get("source", "")),
            query_type,
        )
        enriched["query_aware_reliability"] = True
        query_aware_records.append(enriched)
    return score_and_rank_records(
        query_aware_records,
        bm25_weight=bm25_weight,
        temporal_weight=temporal_weight,
        reliability_weight=reliability_weight,
    )


def is_gold_title_hit(record: dict[str, Any], gold_titles: list[str]) -> bool:
    title = str(record.get("title", "")).lower()
    text = str(record.get("text", "")).lower()
    for gold in gold_titles:
        gold_lower = gold.lower()
        if gold_lower and (gold_lower in title or gold_lower in text):
            return True
    return False


def gold_rank(records: list[dict[str, Any]], gold_titles: list[str], rank_field: str) -> int | None:
    ranked = sorted(records, key=lambda item: int(item.get(rank_field, 10**9)))
    for record in ranked:
        if is_gold_title_hit(record, gold_titles):
            return int(record.get(rank_field, 10**9))
    return None


def classify_failure_reason(
    raw_top1_hit: bool,
    source_order_changed: bool,
    raw_top1_source: str,
    final_top1_source: str,
    gold_closer: str,
    relation: str,
    wiki_overlap: float,
    wikidata_overlap: float,
) -> str:
    if raw_top1_hit:
        return "bm25_already_correct"
    if source_order_changed and raw_top1_source == final_top1_source:
        return "reliability_changed_non-gold_items_only"
    if gold_closer == "wikidata" and final_top1_source == "wikipedia":
        return "source_score_direction_wrong"
    if relation in {"support", "complement"} and gold_closer == "both":
        return "source_difference_not_relevant_to_query"
    if gold_closer in {"wikipedia", "wikidata"}:
        favored_overlap = wiki_overlap if gold_closer == "wikipedia" else wikidata_overlap
        other_overlap = wikidata_overlap if gold_closer == "wikipedia" else wiki_overlap
        if favored_overlap < other_overlap:
            return "supporting_source_has_less_lexical_match"
    return "source_difference_not_relevant_to_query"


def stage_summary(
    grouped_records: dict[str, list[dict[str, Any]]],
    gold_titles_map: dict[str, list[str]],
) -> dict[str, Any]:
    query_ids = sorted(gold_titles_map)
    hits_at = {1: 0, 5: 0, 10: 0}
    source_counts = Counter()
    for query_id in query_ids:
        ranked = grouped_records[query_id]
        if ranked:
            source_counts[normalize_source(str(ranked[0].get("source_name") or ranked[0].get("source", "")))] += 1
        for k in hits_at:
            if any(is_gold_title_hit(record, gold_titles_map[query_id]) for record in ranked[:k]):
                hits_at[k] += 1
    total = max(len(query_ids), 1)
    return {
        "query_count": len(query_ids),
        "top1_hits": hits_at[1],
        "recall_at_1": hits_at[1] / total,
        "recall_at_5": hits_at[5] / total,
        "recall_at_10": hits_at[10] / total,
        "top1_source_counts": dict(source_counts),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze reliability mechanism on the heterogenous-source FEVER subset.")
    parser.add_argument("--queries", required=True, help="Processed query jsonl.")
    parser.add_argument("--corpus", required=True, help="Corpus jsonl.")
    parser.add_argument("--retrieval", required=True, help="Retrieval results jsonl.")
    parser.add_argument("--reranked", required=True, help="Current reranked results jsonl.")
    parser.add_argument("--metrics", required=True, help="Existing metrics json.")
    parser.add_argument("--run-dir", required=True, help="Output run directory.")
    parser.add_argument("--bm25-weight", type=float, default=0.6)
    parser.add_argument("--temporal-weight", type=float, default=0.2)
    parser.add_argument("--reliability-weight", type=float, default=0.2)
    args = parser.parse_args()

    queries = read_jsonl(args.queries)
    retrieval_records = read_jsonl(args.retrieval)
    reranked_records = read_jsonl(args.reranked)
    existing_metrics = read_json(args.metrics)
    run_dir = ensure_dir(args.run_dir)

    retrieval_grouped = group_by_query(retrieval_records, "rank")
    reranked_grouped = group_by_query(reranked_records, "final_rank")

    query_type_map = {str(query["id"]): classify_query_type(str(query["claim"])) for query in queries}
    query_aware_reranked = build_query_aware_records(
        reranked_records,
        query_type_map=query_type_map,
        bm25_weight=args.bm25_weight,
        temporal_weight=args.temporal_weight,
        reliability_weight=args.reliability_weight,
    )
    query_aware_grouped = group_by_query(query_aware_reranked, "final_rank")

    source_relation_rows: list[dict[str, Any]] = []
    paper_rows: list[dict[str, Any]] = []
    failure_cases: list[dict[str, Any]] = []
    relation_counts = Counter({label: 0 for label in RELATION_LABELS})
    failure_reason_counts = Counter({label: 0 for label in FAILURE_REASON_LABELS})
    query_type_counts = Counter(query_type_map.values())
    temporal_nondefault_no_gain = 0
    reliability_changed_source_order_count = 0
    query_aware_changed_top1_count = 0
    query_aware_improved_count = 0
    query_aware_degraded_count = 0

    for query in queries:
        query_id = str(query["id"])
        claim = str(query["claim"])
        gold_titles = [str(item) for item in query.get("evidence_titles") or query.get("evidence") or [] if str(item)]
        raw_records = retrieval_grouped[query_id]
        final_records = reranked_grouped[query_id]
        query_aware_records = query_aware_grouped[query_id]
        wiki_doc = best_record_for_source(raw_records, "wikipedia", "rank")
        wikidata_doc = best_record_for_source(raw_records, "wikidata", "rank")
        if wiki_doc is None or wikidata_doc is None:
            raise KeyError(f"Missing paired sources in retrieval results for query: {query_id}")

        raw_top1 = raw_records[0]
        final_top1 = final_records[0]
        query_aware_top1 = query_aware_records[0]

        raw_top1_source = normalize_source(str(raw_top1.get("source_name") or raw_top1.get("source", "")))
        final_top1_source = normalize_source(str(final_top1.get("source_name") or final_top1.get("source", "")))
        query_aware_top1_source = normalize_source(str(query_aware_top1.get("source_name") or query_aware_top1.get("source", "")))

        wiki_text = str(wiki_doc.get("text", ""))
        wikidata_text = str(wikidata_doc.get("text", ""))
        relation = relation_label(claim, wiki_text, wikidata_text)
        relation_counts[relation] += 1

        wiki_overlap = lexical_overlap(claim, wiki_text)
        wikidata_overlap = lexical_overlap(claim, wikidata_text)
        closer_source = gold_closer_source(claim, wiki_text, wikidata_text)

        raw_order = source_order_signature(raw_records, "rank")
        final_order = source_order_signature(final_records, "final_rank")
        source_order_changed = raw_order != final_order
        reliability_changed_source_order_count += int(source_order_changed)

        raw_gold_rank = gold_rank(raw_records, gold_titles, "rank")
        final_gold_rank = gold_rank(final_records, gold_titles, "final_rank")
        query_aware_gold_rank = gold_rank(query_aware_records, gold_titles, "final_rank")

        raw_top1_hit = raw_gold_rank == 1
        final_top1_hit = final_gold_rank == 1
        query_aware_top1_hit = query_aware_gold_rank == 1

        if query_aware_top1_source != final_top1_source:
            query_aware_changed_top1_count += 1
        if (not final_top1_hit) and query_aware_top1_hit:
            query_aware_improved_count += 1
        if final_top1_hit and (not query_aware_top1_hit):
            query_aware_degraded_count += 1

        has_nondefault_temporal = any(float(record.get("temporal_score", 0.5)) != 0.5 for record in raw_records)
        if has_nondefault_temporal and final_gold_rank == raw_gold_rank:
            temporal_nondefault_no_gain += 1

        top1_not_improved_reason = classify_failure_reason(
            raw_top1_hit=raw_top1_hit,
            source_order_changed=source_order_changed,
            raw_top1_source=raw_top1_source,
            final_top1_source=final_top1_source,
            gold_closer=closer_source,
            relation=relation,
            wiki_overlap=wiki_overlap,
            wikidata_overlap=wikidata_overlap,
        )
        failure_reason_counts[top1_not_improved_reason] += 1

        row = {
            "query_id": query_id,
            "claim": claim,
            "gold_label": query.get("label"),
            "query_type": query_type_map[query_id],
            "relation_label": relation,
            "bm25_top1_source": raw_top1_source,
            "final_top1_source": final_top1_source,
            "query_aware_top1_source": query_aware_top1_source,
            "wikipedia_best_rank": best_rank_for_source(raw_records, "wikipedia", "rank"),
            "wikidata_best_rank": best_rank_for_source(raw_records, "wikidata", "rank"),
            "final_wikipedia_best_rank": best_rank_for_source(final_records, "wikipedia", "final_rank"),
            "final_wikidata_best_rank": best_rank_for_source(final_records, "wikidata", "final_rank"),
            "query_aware_wikipedia_best_rank": best_rank_for_source(query_aware_records, "wikipedia", "final_rank"),
            "query_aware_wikidata_best_rank": best_rank_for_source(query_aware_records, "wikidata", "final_rank"),
            "gold_evidence_closer_source": closer_source,
            "reliability_changed_source_order": source_order_changed,
            "bm25_gold_rank": raw_gold_rank,
            "current_reliability_gold_rank": final_gold_rank,
            "query_aware_gold_rank": query_aware_gold_rank,
            "bm25_top1_hit": raw_top1_hit,
            "current_reliability_top1_hit": final_top1_hit,
            "query_aware_top1_hit": query_aware_top1_hit,
            "wiki_claim_overlap": round(wiki_overlap, 4),
            "wikidata_claim_overlap": round(wikidata_overlap, 4),
            "wiki_reliability_score": base_reliability_score("wikipedia"),
            "wikidata_reliability_score": base_reliability_score("wikidata"),
            "query_aware_wiki_score": query_aware_reliability_score("wikipedia", query_type_map[query_id]),
            "query_aware_wikidata_score": query_aware_reliability_score("wikidata", query_type_map[query_id]),
            "why_no_top1_improvement": top1_not_improved_reason,
        }
        source_relation_rows.append(row)

        paper_rows.append(
            {
                "query_id": query_id,
                "gold_label": query.get("label"),
                "query_type": query_type_map[query_id],
                "relation_label": relation,
                "bm25_top1_source": raw_top1_source,
                "current_reliability_top1_source": final_top1_source,
                "query_aware_top1_source": query_aware_top1_source,
                "gold_closer_source": closer_source,
                "bm25_top1_hit": raw_top1_hit,
                "current_reliability_top1_hit": final_top1_hit,
                "query_aware_top1_hit": query_aware_top1_hit,
                "failure_reason": top1_not_improved_reason,
            }
        )

        failure_cases.append(
            {
                "query_id": query_id,
                "claim": claim,
                "gold_label": query.get("label"),
                "query_type": query_type_map[query_id],
                "relation_label": relation,
                "gold_evidence_closer_source": closer_source,
                "bm25_top1_source": raw_top1_source,
                "final_top1_source": final_top1_source,
                "query_aware_top1_source": query_aware_top1_source,
                "reliability_changed_source_order": source_order_changed,
                "why_no_top1_improvement": top1_not_improved_reason,
            }
        )

    bm25_summary = stage_summary(retrieval_grouped, {str(query["id"]): [str(item) for item in query.get("evidence_titles") or query.get("evidence") or [] if str(item)] for query in queries})
    current_summary = stage_summary(reranked_grouped, {str(query["id"]): [str(item) for item in query.get("evidence_titles") or query.get("evidence") or [] if str(item)] for query in queries})
    query_aware_summary = stage_summary(query_aware_grouped, {str(query["id"]): [str(item) for item in query.get("evidence_titles") or query.get("evidence") or [] if str(item)] for query in queries})

    comparison = {
        "query_count": len(queries),
        "existing_metrics_snapshot": existing_metrics,
        "query_type_counts": dict(query_type_counts),
        "relation_label_counts": dict(relation_counts),
        "failure_reason_counts": dict(failure_reason_counts),
        "reliability_changed_source_order_count": reliability_changed_source_order_count,
        "temporal_nondefault_but_no_rank_gain_count": temporal_nondefault_no_gain,
        "bm25": bm25_summary,
        "current_reliability": current_summary,
        "query_aware_reliability": query_aware_summary,
        "query_aware_top1_source_changed_count": query_aware_changed_top1_count,
        "query_aware_improved_count": query_aware_improved_count,
        "query_aware_degraded_count": query_aware_degraded_count,
    }

    lines = [
        "# Reliability Failure Analysis",
        "",
        f"- Query count: {len(queries)}",
        f"- Query type counts: {dict(query_type_counts)}",
        f"- Source relation labels: {dict(relation_counts)}",
        f"- Failure reasons: {dict(failure_reason_counts)}",
        f"- Reliability changed source order for {reliability_changed_source_order_count} / {len(queries)} queries.",
        f"- Temporal score had non-default values but no rank gain for {temporal_nondefault_no_gain} queries.",
        "",
        "## Comparison",
        "",
        f"- BM25 top1 hits: {bm25_summary['top1_hits']} / {len(queries)}",
        f"- Current reliability top1 hits: {current_summary['top1_hits']} / {len(queries)}",
        f"- Query-aware reliability top1 hits: {query_aware_summary['top1_hits']} / {len(queries)}",
        f"- Query-aware top1 source changes: {query_aware_changed_top1_count}",
        f"- Query-aware improvements: {query_aware_improved_count}",
        f"- Query-aware degradations: {query_aware_degraded_count}",
        "",
        "## Why Current Reliability Has Limited Effect",
        "",
        "- The current rule is source-only: Wikipedia is always scored higher than Wikidata, regardless of claim type.",
        "- The metric is page-level title hit, so many Wikidata top1 results already count as correct if they point to the right page title.",
        "- When BM25 strongly favors Wikidata lexical forms, the 0.15 reliability gap is usually too small to reverse the ordering.",
        "- When both sources point to the same page-level entity, source differences often do not matter for top1 hit under the current metric.",
    ]

    write_jsonl(run_dir / "source_relation_analysis.jsonl", source_relation_rows)
    write_jsonl(run_dir / "failure_cases.jsonl", failure_cases)
    write_json(run_dir / "query_aware_reliability_results.json", comparison)
    write_csv(run_dir / "paper_analysis_table.csv", paper_rows)
    (run_dir / "reliability_failure_analysis.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(comparison, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
