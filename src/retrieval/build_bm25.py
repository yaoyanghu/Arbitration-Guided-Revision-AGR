from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi

from src.common import ensure_dir, read_jsonl, write_json


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def load_corpus(corpus_path: str | Path) -> list[dict[str, Any]]:
    path = Path(corpus_path)
    if not path.exists():
        raise FileNotFoundError(f"Corpus file not found: {path}")
    if path.is_dir():
        corpus: list[dict[str, Any]] = []
        for shard_path in sorted(path.rglob("*.jsonl")):
            corpus.extend(read_jsonl(shard_path))
    else:
        corpus = read_jsonl(path)
    if not corpus:
        raise ValueError(f"Corpus file is empty: {path}")
    return corpus


def iter_corpus_records(corpus_path: str | Path):
    path = Path(corpus_path)
    if not path.exists():
        raise FileNotFoundError(f"Corpus path not found: {path}")
    if path.is_dir():
        for shard_path in sorted(path.rglob("*.jsonl")):
            for record in read_jsonl(shard_path):
                yield record
        return
    for record in read_jsonl(path):
        yield record


def build_bm25_index(corpus: list[dict[str, Any]]) -> dict[str, Any]:
    tokenized_docs = [tokenize(f"{item.get('title', '')} {item.get('text', '')}") for item in corpus]
    if not any(tokenized_docs):
        raise ValueError("Corpus cannot build a BM25 index because all tokenized documents are empty.")
    return {
        "corpus": corpus,
        "tokenized_docs": tokenized_docs,
    }


def save_index(index_dir: str | Path, index_payload: dict[str, Any]) -> Path:
    target_dir = ensure_dir(index_dir)
    payload = {
        "corpus": index_payload["corpus"],
        "tokenized_docs": index_payload["tokenized_docs"],
    }
    index_path = target_dir / "bm25_index.json"
    write_json(index_path, payload)
    return index_path


def save_sqlite_index(corpus_path: str | Path, index_dir: str | Path) -> Path:
    target_dir = ensure_dir(index_dir)
    db_path = target_dir / "bm25_fts.db"
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE docs USING fts5("
            "doc_id UNINDEXED, title, text, source UNINDEXED, timestamp UNINDEXED, "
            "tokenize='unicode61'"
            ")"
        )
        batch: list[tuple[str, str, str, str, str]] = []
        total = 0
        for record in iter_corpus_records(corpus_path):
            batch.append(
                (
                    str(record.get("doc_id", "")),
                    str(record.get("title", "")),
                    str(record.get("text", "")),
                    str(record.get("source", "unknown")),
                    str(record.get("timestamp", "")),
                )
            )
            if len(batch) >= 5000:
                conn.executemany(
                    "INSERT INTO docs (doc_id, title, text, source, timestamp) VALUES (?, ?, ?, ?, ?)",
                    batch,
                )
                conn.commit()
                total += len(batch)
                batch = []
        if batch:
            conn.executemany(
                "INSERT INTO docs (doc_id, title, text, source, timestamp) VALUES (?, ?, ?, ?, ?)",
                batch,
            )
            conn.commit()
            total += len(batch)
        with (target_dir / "bm25_backend.txt").open("w", encoding="utf-8") as handle:
            handle.write("sqlite_fts5\n")
        with (target_dir / "bm25_index_meta.json").open("w", encoding="utf-8") as handle:
            json.dump({"backend": "sqlite_fts5", "document_count": total}, handle, ensure_ascii=False, indent=2)
    finally:
        conn.close()
    return db_path


def build_and_save_index(corpus_path: str | Path, index_dir: str | Path, backend: str = "auto") -> Path:
    corpus_source = Path(corpus_path)
    selected_backend = backend
    if backend == "auto":
        selected_backend = "sqlite" if corpus_source.is_dir() else "json"
    if selected_backend == "sqlite":
        return save_sqlite_index(corpus_path, index_dir)
    corpus = load_corpus(corpus_path)
    index_payload = build_bm25_index(corpus)
    return save_index(index_dir, index_payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a BM25 index from a corpus jsonl file.")
    parser.add_argument("--corpus-path", required=True, help="Path to corpus jsonl.")
    parser.add_argument("--index-dir", required=True, help="Directory to store the BM25 index.")
    parser.add_argument(
        "--backend",
        choices=["auto", "json", "sqlite"],
        default="auto",
        help="BM25 backend. Use sqlite for large official FEVER corpora.",
    )
    args = parser.parse_args()
    index_path = build_and_save_index(args.corpus_path, args.index_dir, backend=args.backend)
    print(f"Saved BM25 index to {index_path.resolve()}")


if __name__ == "__main__":
    main()
