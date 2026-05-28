from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any, Callable

from src.analysis.nearest_title_baseline_eval import exact_title_match_score
from src.analysis.official_strict_revalidation import (
    canonical_title,
    compute_metrics,
    group_by_query,
    relaxed_hit,
    strict_hit,
)
from src.analysis.official_title_overlap_improvement import (
    PAREN_PATTERN,
    normalize_bm25,
    title_overlap_score,
)
from src.common import ensure_dir, read_jsonl, write_json, write_jsonl

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")
TYPE_WORDS = {
    "actor",
    "album",
    "band",
    "city",
    "comedian",
    "film",
    "novel",
    "record",
    "series",
    "show",
    "song",
    "television",
    "tv",
}
ALIAS_PATTERNS = [
    re.compile(r"\b(?:also known as|known as|aka|alias(?:es)?|nicknamed)\b([^.;:]+)", re.IGNORECASE),
    re.compile(r"\b(?:called|spelled as)\b([^.;:]+)", re.IGNORECASE),
]


def normalize_text(text: str) -> str:
    normalized = canonical_title(text)
    normalized = re.sub(r"[^a-z0-9()\[\]{}\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def normalized_phrase(text: str) -> str:
    normalized = normalize_text(text)
    return f" {normalized} " if normalized else " "


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(normalize_text(text))


def base_title(title: str) -> str:
    return PAREN_PATTERN.sub("", title).strip()


def parenthetical_qualifier(title: str) -> str:
    match = re.search(r"\(([^)]*)\)", title)
    return match.group(1).strip() if match else ""


def split_alias_chunk(text: str) -> list[str]:
    cleaned = text.replace(" or ", ",").replace(" and ", ",")
    parts = re.split(r"[,/]|(?:\s+-\s+)", cleaned)
    aliases: list[str] = []
    for part in parts:
        alias = part.strip(" \"'`()[]{}")
        if not alias:
            continue
        if len(alias) < 3:
            continue
        aliases.append(alias)
    return aliases


def quoted_aliases(text: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"['\"“”]([^'\"“”]{3,60})['\"“”]", text)]


def extract_alias_candidates(title: str, doc_id: str, text: str) -> list[str]:
    candidates: set[str] = set()
    title_norm = normalize_text(title)
    base_norm = normalize_text(base_title(title))
    for raw in (title, base_title(title), doc_id.replace("_", " ")):
        raw = raw.strip()
        if raw:
            candidates.add(raw)

    text_window = text[:350]
    for pattern in ALIAS_PATTERNS:
        for match in pattern.finditer(text_window):
            for alias in split_alias_chunk(match.group(1)):
                alias_norm = normalize_text(alias)
                if alias_norm and alias_norm not in {title_norm, base_norm}:
                    candidates.add(alias)
    for alias in quoted_aliases(text_window):
        alias_norm = normalize_text(alias)
        if alias_norm and alias_norm not in {title_norm, base_norm}:
            candidates.add(alias)
    return sorted(candidates)


def alias_redirect_match_score(query: str, title: str, doc_id: str, text: str) -> float:
    query_text = normalized_phrase(query)
    title_norm = normalize_text(title)
    base_norm = normalize_text(base_title(title))
    alias_hits = 0
    best_len = 0
    for alias in extract_alias_candidates(title, doc_id, text):
        alias_norm = normalize_text(alias)
        if not alias_norm or alias_norm in {title_norm, base_norm}:
            continue
        phrase = f" {alias_norm} "
        if phrase in query_text:
            alias_hits += 1
            best_len = max(best_len, len(alias_norm.split()))
    if alias_hits == 0:
        return 0.0
    return min(1.0, 0.6 + 0.1 * best_len + 0.1 * min(alias_hits, 2))


def disambiguation_title_match_score(query: str, title: str, doc_id: str, text: str) -> float:
    del doc_id, text
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return 0.0
    qualifier = parenthetical_qualifier(title)
    if not qualifier:
        return 0.0
    qualifier_norm = normalize_text(qualifier)
    if qualifier_norm == "disambiguation":
        return 0.0
    base_phrase = normalized_phrase(base_title(title))
    query_phrase = normalized_phrase(query)
    qualifier_tokens = set(tokenize(qualifier))
    if not qualifier_tokens:
        return 0.0
    overlap = len(query_tokens & qualifier_tokens) / len(qualifier_tokens)
    if overlap <= 0:
        return 0.0
    score = 0.5 * overlap
    if base_phrase.strip() and base_phrase in query_phrase:
        score += 0.5
    return min(1.0, score)


def as_query_rows(predictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in predictions:
        rows.append(
            {
                "id": str(item["id"]),
                "claim": item.get("claim", ""),
                "label": item.get("gold_label", ""),
                "evidence_titles": [str(x) for x in item.get("gold_evidence", []) if str(x)],
            }
        )
    return rows


def top1_title(grouped_records: dict[str, list[dict[str, Any]]], query_id: str, rank_field: str) -> str | None:
    items = grouped_records.get(query_id, [])
    if not items:
        return None
    top1 = sorted(items, key=lambda item: int(item[rank_field]))[0]
    return str(top1.get("title"))


def build_rerank(
    retrieval_records: list[dict[str, Any]],
    bm25_weight: float,
    metadata_weight: float,
    feature_name: str,
    score_fn: Callable[[str, str, str, str], float],
) -> list[dict[str, Any]]:
    enriched_records = normalize_bm25(retrieval_records)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in enriched_records:
        feature_score = score_fn(
            str(record.get("query", "")),
            str(record.get("title", "")),
            str(record.get("doc_id", "")),
            str(record.get("text", "")),
        )
        updated = dict(record)
        updated[f"{feature_name}_score"] = feature_score
        updated[f"{feature_name}_rerank_score"] = (
            bm25_weight * float(record["bm25_score_norm"]) + metadata_weight * feature_score
        )
        grouped[str(record["query_id"])].append(updated)

    reranked_records: list[dict[str, Any]] = []
    for query_id, items in grouped.items():
        reranked = sorted(
            items,
            key=lambda item: (
                float(item[f"{feature_name}_rerank_score"]),
                float(item.get("bm25_score_norm", 0.0)),
            ),
            reverse=True,
        )
        for rank, item in enumerate(reranked, start=1):
            item[f"{feature_name}_rank"] = rank
            reranked_records.append(item)
    return reranked_records


def variant_case_lists(
    queries: list[dict[str, Any]],
    baseline_grouped: dict[str, list[dict[str, Any]]],
    variant_grouped: dict[str, list[dict[str, Any]]],
    baseline_metrics: dict[str, Any],
    variant_metrics: dict[str, Any],
    variant_name: str,
    rank_field: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    improved: list[dict[str, Any]] = []
    regressed: list[dict[str, Any]] = []
    for query in queries:
        query_id = str(query["id"])
        baseline_rank = baseline_metrics["per_query_ranks"][query_id]
        variant_rank = variant_metrics["per_query_ranks"][query_id]
        row = {
            "query_id": query_id,
            "claim": query.get("claim"),
            "gold_label": query.get("label"),
            "gold_titles": [str(x) for x in query.get("evidence_titles", []) if str(x)],
            "baseline_top1_title": top1_title(baseline_grouped, query_id, "rank"),
            "variant_top1_title": top1_title(variant_grouped, query_id, rank_field),
            "baseline_strict_rank": baseline_rank,
            "variant_strict_rank": variant_rank,
            "variant_name": variant_name,
        }
        if baseline_rank != 1 and variant_rank == 1:
            improved.append(row)
        if baseline_rank == 1 and variant_rank != 1:
            regressed.append(row)
    return improved, regressed


def compute_labelwise_strict(
    queries: list[dict[str, Any]],
    grouped_records: dict[str, list[dict[str, Any]]],
    rank_field: str,
) -> dict[str, dict[str, Any]]:
    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for query in queries:
        by_label[str(query.get("label", "UNKNOWN"))].append(query)
    results: dict[str, dict[str, Any]] = {}
    for label, label_queries in by_label.items():
        metrics = compute_metrics(grouped_records, label_queries, strict_hit, rank_field)
        results[label] = {
            "count": len(label_queries),
            "strict_recall_at_1": metrics["recall_at_1"],
            "strict_recall_at_5": metrics["recall_at_5"],
            "strict_recall_at_10": metrics["recall_at_10"],
            "strict_top1_hits": metrics["top1_hits"],
        }
    return results


def claim_type_tags(claim: str) -> list[str]:
    tags: list[str] = []
    claim_norm = normalize_text(claim)
    claim_tokens = set(tokenize(claim))
    if any(word in claim_tokens for word in TYPE_WORDS):
        tags.append("type_word")
    if any(marker in claim_norm for marker in ("also known as", "known as", "aka", "alias")):
        tags.append("alias_cue")
    if "(" in claim or ")" in claim:
        tags.append("parenthetical_surface")
    if not tags:
        tags.append("plain_entity_surface")
    return tags


def summarize_claim_types(cases: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for item in cases:
        for tag in claim_type_tags(str(item.get("claim", ""))):
            counter[tag] += 1
    return dict(counter.most_common())


def summarize_variant_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "recall_at_1": metrics["recall_at_1"],
        "recall_at_5": metrics["recall_at_5"],
        "recall_at_10": metrics["recall_at_10"],
        "top1_hits": metrics["top1_hits"],
    }


def write_summary_markdown(result: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# Metadata Family Summary",
        "",
        "## Settings",
        "",
        f"- source run: `{result['source_run_dir']}`",
        f"- bm25 weight: `{result['weights']['bm25_weight']}`",
        f"- metadata weight: `{result['weights']['metadata_weight']}`",
        "",
        "## Main Family Table",
        "",
        "| variant | strict R@1 / R@5 / R@10 | relaxed R@1 / R@5 / R@10 | improved / regressed |",
        "| --- | --- | --- | ---: |",
        f"| routeA_bm25 | {result['baseline']['strict']['recall_at_1']:.3f} / {result['baseline']['strict']['recall_at_5']:.3f} / {result['baseline']['strict']['recall_at_10']:.3f} | {result['baseline']['relaxed']['recall_at_1']:.3f} / {result['baseline']['relaxed']['recall_at_5']:.3f} / {result['baseline']['relaxed']['recall_at_10']:.3f} | 0 / 0 |",
    ]
    for variant_name, payload in result["variants"].items():
        lines.append(
            f"| {variant_name} | {payload['strict']['recall_at_1']:.3f} / {payload['strict']['recall_at_5']:.3f} / {payload['strict']['recall_at_10']:.3f} | {payload['relaxed']['recall_at_1']:.3f} / {payload['relaxed']['recall_at_5']:.3f} / {payload['relaxed']['recall_at_10']:.3f} | {payload['strict_improved_case_count']} / {payload['strict_regressed_case_count']} |"
        )
    lines.extend(
        [
            "",
            "## Initial Diagnosis",
            "",
        ]
    )
    for variant_name, payload in result["variants"].items():
        lines.append(f"### {variant_name}")
        lines.append("")
        lines.append(f"- improved claim tags: `{payload['diagnosis']['improved_claim_tags']}`")
        lines.append(f"- regressed claim tags: `{payload['diagnosis']['regressed_claim_tags']}`")
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate lightweight metadata-aware reranking variants on an existing FEVER run.")
    parser.add_argument("--source-run-dir", required=True)
    parser.add_argument("--output-run-dir", required=True)
    parser.add_argument("--bm25-weight", type=float, default=0.5)
    parser.add_argument("--metadata-weight", type=float, default=0.5)
    parser.add_argument(
        "--variants",
        nargs="+",
        default=[
            "title_overlap",
            "exact_title_boost",
            "alias_redirect_match",
            "disambiguation_title_match",
        ],
    )
    args = parser.parse_args()

    feature_fns: dict[str, Callable[[str, str, str, str], float]] = {
        "title_overlap": lambda q, t, d, x: title_overlap_score(q, t),
        "exact_title_boost": lambda q, t, d, x: exact_title_match_score(q, t),
        "alias_redirect_match": alias_redirect_match_score,
        "disambiguation_title_match": disambiguation_title_match_score,
    }

    source_run_dir = Path(args.source_run_dir)
    output_run_dir = ensure_dir(args.output_run_dir)
    retrieval_records = read_jsonl(source_run_dir / "retrieval_results.jsonl")
    predictions = read_jsonl(source_run_dir / "predictions.jsonl")
    queries = as_query_rows(predictions)

    baseline_grouped = group_by_query(retrieval_records, "rank")
    baseline_strict = compute_metrics(baseline_grouped, queries, strict_hit, "rank")
    baseline_relaxed = compute_metrics(baseline_grouped, queries, relaxed_hit, "rank")

    result: dict[str, Any] = {
        "source_run_dir": str(source_run_dir),
        "weights": {
            "bm25_weight": args.bm25_weight,
            "metadata_weight": args.metadata_weight,
        },
        "baseline": {
            "strict": summarize_variant_metrics(baseline_strict),
            "relaxed": summarize_variant_metrics(baseline_relaxed),
        },
        "variants": {},
    }

    for variant_name in args.variants:
        if variant_name not in feature_fns:
            raise ValueError(f"Unsupported variant: {variant_name}")
        reranked_records = build_rerank(
            retrieval_records=retrieval_records,
            bm25_weight=args.bm25_weight,
            metadata_weight=args.metadata_weight,
            feature_name=variant_name,
            score_fn=feature_fns[variant_name],
        )
        rank_field = f"{variant_name}_rank"
        grouped = group_by_query(reranked_records, rank_field)
        strict_metrics = compute_metrics(grouped, queries, strict_hit, rank_field)
        relaxed_metrics = compute_metrics(grouped, queries, relaxed_hit, rank_field)
        improved_cases, regressed_cases = variant_case_lists(
            queries=queries,
            baseline_grouped=baseline_grouped,
            variant_grouped=grouped,
            baseline_metrics=baseline_strict,
            variant_metrics=strict_metrics,
            variant_name=variant_name,
            rank_field=rank_field,
        )
        write_jsonl(output_run_dir / f"{variant_name}_reranked_results.jsonl", reranked_records)
        write_jsonl(output_run_dir / f"{variant_name}_strict_improved_cases.jsonl", improved_cases)
        write_jsonl(output_run_dir / f"{variant_name}_strict_regressed_cases.jsonl", regressed_cases)
        result["variants"][variant_name] = {
            "strict": summarize_variant_metrics(strict_metrics),
            "relaxed": summarize_variant_metrics(relaxed_metrics),
            "strict_improved_case_count": len(improved_cases),
            "strict_regressed_case_count": len(regressed_cases),
            "strict_top1_delta": strict_metrics["top1_hits"] - baseline_strict["top1_hits"],
            "labelwise_strict": compute_labelwise_strict(queries, grouped, rank_field),
            "diagnosis": {
                "improved_claim_tags": summarize_claim_types(improved_cases),
                "regressed_claim_tags": summarize_claim_types(regressed_cases),
            },
        }

    write_json(output_run_dir / "family_results.json", result)
    write_summary_markdown(result, output_run_dir / "family_summary.md")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
