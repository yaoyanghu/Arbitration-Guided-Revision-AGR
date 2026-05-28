from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.common import ensure_dir, write_jsonl
from src.data.prepare_fever import decode_fever_title

REQUIRED_FIELDS = ("doc_id", "title", "text", "source")
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"


def _load_records(path: str | Path) -> list[dict[str, Any]]:
    input_path = Path(path)
    if not input_path.exists():
        raise FileNotFoundError(
            f"Corpus input not found: {input_path}\n"
            "Expected jsonl with fields: doc_id, title, text, source, optional timestamp."
        )
    records: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            missing = [field for field in REQUIRED_FIELDS if field not in payload]
            if missing:
                raise ValueError(
                    f"Corpus record is missing required fields {missing}. "
                    "Expected jsonl fields: doc_id, title, text, source, optional timestamp."
                )
            records.append(
                {
                    "doc_id": str(payload["doc_id"]),
                    "title": str(payload["title"]).strip(),
                    "text": str(payload["text"]).strip(),
                    "source": str(payload["source"]).strip() or "unknown",
                    "timestamp": str(payload.get("timestamp", "")).strip(),
                }
            )
    return records


def build_corpus(input_path: str | Path, output_path: str | Path) -> list[dict[str, Any]]:
    records = _load_records(input_path)
    target = Path(output_path)
    ensure_dir(target.parent)
    write_jsonl(target, records)
    return records


def _iter_jsonl_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def write_demo_corpus(output_path: str | Path) -> list[dict[str, Any]]:
    demo_input = Path("data/demo/demo_corpus_source.jsonl")
    records = _load_records(demo_input)
    target = Path(output_path)
    ensure_dir(target.parent)
    write_jsonl(target, records)
    return records


def _load_fever_titles(path: str | Path) -> list[str]:
    fever_path = Path(path)
    if not fever_path.exists():
        raise FileNotFoundError(f"Processed FEVER file not found: {fever_path}")
    titles: list[str] = []
    with fever_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            for title in payload.get("evidence_titles", payload.get("evidence", [])):
                normalized = decode_fever_title(str(title).strip())
                if normalized and normalized not in titles:
                    titles.append(normalized)
    if not titles:
        raise ValueError("No FEVER evidence titles found in the processed file.")
    return titles


def _fetch_wikipedia_extracts(titles: list[str]) -> list[dict[str, Any]]:
    import requests

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "ChronoRAG/0.1 (research experiment setup; contact: local-run)",
            "Accept": "application/json",
        }
    )
    records: list[dict[str, Any]] = []
    for title in titles:
        summary_response = session.get(
            WIKIPEDIA_SUMMARY_URL + requests.utils.quote(title, safe=""),
            timeout=60,
        )
        if summary_response.status_code != 200:
            continue
        summary_payload = summary_response.json()
        extract = str(summary_payload.get("extract", "")).strip()
        normalized_title = str(summary_payload.get("title", title)).strip()
        page_id = summary_payload.get("pageid", normalized_title)
        if not extract:
            continue
        records.append(
            {
                "doc_id": str(page_id),
                "title": normalized_title,
                "text": extract,
                "source": "wikipedia_api_summary",
                "timestamp": "",
            }
        )
    cleaned = [record for record in records if record["text"]]
    if not cleaned:
        raise ValueError("Wikipedia API returned no usable page text for the requested FEVER titles.")
    return cleaned


def build_corpus_from_fever_titles(fever_path: str | Path, output_path: str | Path) -> list[dict[str, Any]]:
    titles = _load_fever_titles(fever_path)
    records = _fetch_wikipedia_extracts(titles)
    target = Path(output_path)
    ensure_dir(target.parent)
    write_jsonl(target, records)
    return records


def _normalize_official_wiki_record(payload: dict[str, Any]) -> dict[str, Any] | None:
    raw_id = str(payload.get("id", "")).strip()
    raw_text = str(payload.get("text", "")).strip()
    if not raw_id or not raw_text:
        return None
    return {
        "doc_id": raw_id,
        "title": decode_fever_title(raw_id),
        "text": raw_text,
        "source": "fever_official_wiki_2017",
        "timestamp": "2017-06",
    }


def build_corpus_from_official_wiki(input_dir: str | Path, output_dir: str | Path) -> dict[str, int]:
    source_dir = Path(input_dir)
    if not source_dir.exists():
        raise FileNotFoundError(f"Official FEVER wiki directory not found: {source_dir}")
    shard_paths = sorted(source_dir.rglob("wiki-*.jsonl"))
    if not shard_paths:
        raise FileNotFoundError(
            f"No official FEVER wiki shard files found under: {source_dir}\n"
            "Expected files like wiki-001.jsonl ... wiki-221.jsonl."
        )
    target_dir = ensure_dir(output_dir)
    total_docs = 0
    total_shards = 0
    for shard_path in shard_paths:
        shard_records = _iter_jsonl_records(shard_path)
        normalized_records: list[dict[str, Any]] = []
        for payload in shard_records:
            normalized = _normalize_official_wiki_record(payload)
            if normalized is None:
                continue
            normalized_records.append(normalized)
        if not normalized_records:
            continue
        write_jsonl(target_dir / shard_path.name, normalized_records)
        total_docs += len(normalized_records)
        total_shards += 1
    return {"shard_count": total_shards, "document_count": total_docs}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build or validate a normalized corpus interface.")
    parser.add_argument(
        "--input",
        default=None,
        help="Path to corpus jsonl. Required unless --use-demo is set.",
    )
    parser.add_argument(
        "--output",
        default="data/corpus/demo_corpus.jsonl",
        help="Path to normalized corpus jsonl.",
    )
    parser.add_argument(
        "--use-demo",
        action="store_true",
        help="Use the bundled demo corpus instead of a real Wikipedia 2018 input.",
    )
    parser.add_argument(
        "--from-fever-processed",
        default=None,
        help="Build a minimal real corpus by fetching Wikipedia pages for FEVER evidence titles.",
    )
    parser.add_argument(
        "--official-wiki-dir",
        default=None,
        help="Path to official FEVER wiki-pages directory containing wiki-*.jsonl shards.",
    )
    args = parser.parse_args()
    if args.use_demo:
        records = write_demo_corpus(args.output)
        print(f"Wrote demo corpus with {len(records)} records to {Path(args.output).resolve()}")
        return
    if args.from_fever_processed:
        records = build_corpus_from_fever_titles(args.from_fever_processed, args.output)
        print(f"Wrote FEVER-derived real corpus with {len(records)} records to {Path(args.output).resolve()}")
        return
    if args.official_wiki_dir:
        summary = build_corpus_from_official_wiki(args.official_wiki_dir, args.output)
        print(
            "Wrote official FEVER corpus shards to "
            f"{Path(args.output).resolve()} "
            f"(shards={summary['shard_count']}, documents={summary['document_count']})"
        )
        return
    if not args.input:
        raise FileNotFoundError(
            "No corpus input provided. Pass --input <corpus.jsonl> or use --use-demo.\n"
            "Expected jsonl fields: doc_id, title, text, source, optional timestamp."
        )
    records = build_corpus(args.input, args.output)
    print(f"Wrote {len(records)} corpus records to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
