from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.common import read_json, read_jsonl, write_json, write_jsonl

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
}

CAUSES = [
    "gold_page_not_in_corpus",
    "gold_page_in_corpus_but_not_recalled",
    "alias_or_title_normalization_mismatch",
    "related_page_recalled_but_wrong_top1",
    "large_lexical_gap_between_query_and_gold_page",
    "other",
]

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")
PAREN_PATTERN = re.compile(r"\s*\([^)]*\)")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def content_tokens(text: str) -> set[str]:
    return {token for token in tokenize(text) if token not in STOPWORDS}


def normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    lowered = lowered.replace("-lrb-", "(").replace("-rrb-", ")")
    lowered = lowered.replace("_", " ")
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def base_title(title: str) -> str:
    return PAREN_PATTERN.sub("", normalize_text(title)).strip()


def lexical_overlap(left: str, right: str) -> float:
    left_tokens = content_tokens(left)
    if not left_tokens:
        return 0.0
    right_tokens = content_tokens(right)
    return len(left_tokens & right_tokens) / len(left_tokens)


def title_similarity(left: str, right: str) -> float:
    left_tokens = content_tokens(base_title(left))
    right_tokens = content_tokens(base_title(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / max(len(left_tokens | right_tokens), 1)


def exact_title_exists(conn: sqlite3.Connection, title: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM docs WHERE lower(title) = lower(?) LIMIT 1",
        (title,),
    ).fetchone()
    return row is not None


def normalized_title_exists(conn: sqlite3.Connection, title: str) -> bool:
    row = conn.execute(
        "SELECT title FROM docs WHERE lower(replace(title, '_', ' ')) = lower(?) LIMIT 1",
        (normalize_text(title),),
    ).fetchone()
    return row is not None


def fetch_related_titles(conn: sqlite3.Connection, title: str, limit: int = 20) -> list[str]:
    tokens = list(content_tokens(base_title(title)))
    if not tokens:
        return []
    match_query = " OR ".join(f'"{token}"' for token in tokens)
    rows = conn.execute(
        "SELECT title FROM docs WHERE docs MATCH ? LIMIT ?",
        (match_query, limit),
    ).fetchall()
    return [str(row[0]) for row in rows]


def best_gold_title(gold_titles: list[str], query: str) -> str:
    if not gold_titles:
        return ""
    return max(gold_titles, key=lambda title: lexical_overlap(query, title))


def top1_doc(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not records:
        return None
    return sorted(records, key=lambda item: int(item["rank"]))[0]


def group_by_query(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["query_id"])].append(record)
    for query_id, items in grouped.items():
        grouped[query_id] = sorted(items, key=lambda item: int(item["rank"]))
    return dict(grouped)


def analyze_miss(
    conn: sqlite3.Connection,
    query_id: str,
    claim: str,
    gold_titles: list[str],
    retrieved: list[dict[str, Any]],
) -> dict[str, Any]:
    top1 = top1_doc(retrieved)
    primary_gold = best_gold_title(gold_titles, claim)
    exact_exists = any(exact_title_exists(conn, title) for title in gold_titles)
    normalized_exists = any(normalized_title_exists(conn, title) for title in gold_titles)
    related_titles = []
    for title in gold_titles:
        related_titles.extend(fetch_related_titles(conn, title))
    related_titles = list(dict.fromkeys(related_titles))
    top_titles = [str(item.get("title", "")) for item in retrieved]
    top1_title = str(top1.get("title", "")) if top1 else ""
    gold_title_overlap = lexical_overlap(claim, primary_gold)
    top1_to_gold_similarity = max((title_similarity(top1_title, title) for title in gold_titles), default=0.0)
    related_title_present = any(
        max(title_similarity(retrieved_title, gold_title) for gold_title in gold_titles) >= 0.5
        for retrieved_title in top_titles
    )

    cause = "other"
    if not exact_exists:
        cause = "alias_or_title_normalization_mismatch" if normalized_exists or related_titles else "gold_page_not_in_corpus"
    elif gold_title_overlap < 0.34:
        cause = "large_lexical_gap_between_query_and_gold_page"
    elif related_title_present or top1_to_gold_similarity >= 0.5:
        cause = "alias_or_title_normalization_mismatch"
    else:
        cause = "gold_page_in_corpus_but_not_recalled"

    return {
        "query_id": query_id,
        "claim": claim,
        "gold_titles": gold_titles,
        "top1_title": top1_title,
        "top10_titles": top_titles,
        "exact_gold_title_in_corpus": exact_exists,
        "normalized_gold_title_in_corpus": normalized_exists,
        "query_gold_title_overlap": round(gold_title_overlap, 4),
        "top1_to_gold_title_similarity": round(top1_to_gold_similarity, 4),
        "related_titles_sample": related_titles[:10],
        "primary_cause": cause,
    }


def analyze_top1_wrong_top10_hit(
    query_id: str,
    claim: str,
    gold_titles: list[str],
    retrieved: list[dict[str, Any]],
    gold_rank: int,
) -> dict[str, Any]:
    top1 = top1_doc(retrieved)
    top1_title = str(top1.get("title", "")) if top1 else ""
    gold_title = best_gold_title(gold_titles, claim)
    title_sim = max((title_similarity(top1_title, title) for title in gold_titles), default=0.0)
    pattern = "other"
    if len(gold_titles) > 1:
        pattern = "multi_page_claim"
    elif title_sim >= 0.5:
        pattern = "related_page_recalled_but_wrong_top1"
    elif lexical_overlap(claim, gold_title) < 0.34:
        pattern = "large_lexical_gap_between_query_and_gold_page"
    else:
        pattern = "entity_or_relation_ambiguity"
    return {
        "query_id": query_id,
        "claim": claim,
        "gold_titles": gold_titles,
        "gold_rank": gold_rank,
        "top1_title": top1_title,
        "top10_titles": [str(item.get("title", "")) for item in retrieved[:10]],
        "pattern": pattern,
        "top1_to_gold_title_similarity": round(title_sim, 4),
        "query_gold_title_overlap": round(lexical_overlap(claim, gold_title), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze official FEVER Route A baseline failures.")
    parser.add_argument("--run-dir", required=True, help="Run directory containing metrics and retrieval outputs.")
    parser.add_argument("--index-db", required=True, help="Path to official SQLite BM25 index.")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    metrics = read_json(run_dir / "metrics.json")
    retrieval_records = read_jsonl(run_dir / "retrieval_results.jsonl")
    error_cases = read_jsonl(run_dir / "error_cases.jsonl")
    predictions = read_jsonl(run_dir / "predictions.jsonl") if (run_dir / "predictions.jsonl").exists() else []

    prediction_by_id = {str(item["id"]): item for item in predictions}
    retrieval_by_id = group_by_query(retrieval_records)

    label_breakdown = {
        "SUPPORTS": {
            "recall_at_1": metrics["stages"]["bm25"]["label_group_hit_rate_at_1"]["SUPPORTS"]["hit_rate_at_1"],
            "recall_at_5": metrics["stages"]["bm25"]["label_group_hit_rate_at_5"]["SUPPORTS"]["hit_rate_at_5"],
            "recall_at_10": metrics["stages"]["bm25"]["label_group_hit_rate_at_10"]["SUPPORTS"]["hit_rate_at_10"],
            "count": metrics["stages"]["bm25"]["label_group_hit_rate_at_1"]["SUPPORTS"]["count"],
        },
        "REFUTES": {
            "recall_at_1": metrics["stages"]["bm25"]["label_group_hit_rate_at_1"]["REFUTES"]["hit_rate_at_1"],
            "recall_at_5": metrics["stages"]["bm25"]["label_group_hit_rate_at_5"]["REFUTES"]["hit_rate_at_5"],
            "recall_at_10": metrics["stages"]["bm25"]["label_group_hit_rate_at_10"]["REFUTES"]["hit_rate_at_10"],
            "count": metrics["stages"]["bm25"]["label_group_hit_rate_at_1"]["REFUTES"]["count"],
        },
    }

    miss_rows: list[dict[str, Any]] = []
    top1_wrong_rows: list[dict[str, Any]] = []
    miss_cause_counts = Counter({cause: 0 for cause in CAUSES})
    top1_wrong_patterns = Counter()
    gold_in_corpus_count = 0
    lexical_gap_count = 0

    conn = sqlite3.connect(args.index_db)
    try:
        for error in error_cases:
            query_id = str(error["id"])
            prediction = prediction_by_id[query_id]
            gold_titles = [str(item) for item in prediction.get("gold_evidence", []) if str(item)]
            retrieved = retrieval_by_id.get(query_id, [])
            analyzed = analyze_miss(conn, query_id, str(prediction["claim"]), gold_titles, retrieved)
            analyzed["gold_label"] = prediction.get("gold_label")
            analyzed["case_kind"] = "retrieval_miss"
            miss_rows.append(analyzed)
            miss_cause_counts[analyzed["primary_cause"]] += 1
            gold_in_corpus_count += int(analyzed["exact_gold_title_in_corpus"])
            lexical_gap_count += int(analyzed["primary_cause"] == "large_lexical_gap_between_query_and_gold_page")

        for prediction in predictions:
            query_id = str(prediction["id"])
            bm25_rank = prediction.get("bm25_rank")
            if bm25_rank is None or bm25_rank == 1 or bm25_rank > 10:
                continue
            gold_titles = [str(item) for item in prediction.get("gold_evidence", []) if str(item)]
            retrieved = retrieval_by_id.get(query_id, [])
            analyzed = analyze_top1_wrong_top10_hit(
                query_id=query_id,
                claim=str(prediction["claim"]),
                gold_titles=gold_titles,
                retrieved=retrieved,
                gold_rank=int(bm25_rank),
            )
            analyzed["gold_label"] = prediction.get("gold_label")
            top1_wrong_rows.append(analyzed)
            top1_wrong_patterns[analyzed["pattern"]] += 1
    finally:
        conn.close()

    total_misses = max(len(miss_rows), 1)
    top1_wrong_count = len(top1_wrong_rows)
    official_failure_cases = miss_rows + top1_wrong_rows
    write_jsonl(run_dir / "official_failure_cases.jsonl", official_failure_cases)

    label_breakdown["miss_summary"] = {
        "retrieval_miss_count": len(miss_rows),
        "gold_page_in_corpus_but_not_recalled_ratio": gold_in_corpus_count / total_misses,
        "large_lexical_gap_between_query_and_gold_page_ratio": lexical_gap_count / total_misses,
        "miss_cause_counts": dict(miss_cause_counts),
    }
    label_breakdown["top1_wrong_but_top10_hit_summary"] = {
        "count": top1_wrong_count,
        "pattern_counts": dict(top1_wrong_patterns),
    }
    write_json(run_dir / "official_label_breakdown.json", label_breakdown)

    title_issue_count = miss_cause_counts["alias_or_title_normalization_mismatch"]
    lines = [
        "# Official FEVER 500 Baseline Failure Analysis",
        "",
        "## Label Breakdown",
        "",
        f"- SUPPORTS Recall@1 / Recall@5 / Recall@10: {label_breakdown['SUPPORTS']['recall_at_1']:.4f} / {label_breakdown['SUPPORTS']['recall_at_5']:.4f} / {label_breakdown['SUPPORTS']['recall_at_10']:.4f}",
        f"- REFUTES Recall@1 / Recall@5 / Recall@10: {label_breakdown['REFUTES']['recall_at_1']:.4f} / {label_breakdown['REFUTES']['recall_at_5']:.4f} / {label_breakdown['REFUTES']['recall_at_10']:.4f}",
        "",
        "## Retrieval Misses",
        "",
        f"- Total retrieval_miss cases: {len(miss_rows)}",
        f"- Miss cause counts: {dict(miss_cause_counts)}",
        f"- Gold page in corpus but BM25 did not recall it: {gold_in_corpus_count}/{len(miss_rows)} ({gold_in_corpus_count / total_misses:.4f})",
        f"- Large lexical gap between query and gold page title: {lexical_gap_count}/{len(miss_rows)} ({lexical_gap_count / total_misses:.4f})",
        "",
        "## Title / Alias / Redirect",
        "",
        f"- Heuristic title-or-alias mismatch cases among misses: {title_issue_count}/{len(miss_rows)}",
        "- Redirects cannot be directly verified from the current FEVER wiki-pages corpus because it does not expose a redirect table in the normalized corpus we built.",
        "- The title/alias estimate here is therefore heuristic: exact title missing or a closely related title variant/disambiguation page dominating retrieval.",
        "",
        "## Top1 Wrong But Top10 Hit",
        "",
        f"- Count: {top1_wrong_count}",
        f"- Pattern counts: {dict(top1_wrong_patterns)}",
        "- These cases are the strongest candidates for a lightweight Recall@1 improvement, because the gold page is already in the retrieved set.",
    ]
    (run_dir / "official_failure_analysis.md").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "miss_cause_counts": dict(miss_cause_counts),
        "top1_wrong_but_top10_hit_count": top1_wrong_count,
        "top1_wrong_pattern_counts": dict(top1_wrong_patterns),
        "gold_page_in_corpus_but_not_recalled_ratio": gold_in_corpus_count / total_misses,
        "large_lexical_gap_ratio": lexical_gap_count / total_misses,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
