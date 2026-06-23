from __future__ import annotations

from typing import Any


def format_evidence(evidence: list[dict[str, Any]], top_k: int = 2, max_chars: int = 1800) -> str:
    blocks: list[str] = []
    for index, row in enumerate(evidence[:top_k], 1):
        title = str(row.get("title", row.get("doc_id", ""))).strip()
        timestamp = str(row.get("timestamp", row.get("date", "")) or "N/A").strip()
        text = " ".join(str(row.get("text", "")).split())[:max_chars]
        blocks.append(f"Evidence {index}:\nTitle: {title}\nTimestamp: {timestamp}\nText: {text}")
    return "\n\n".join(blocks)


def evidence_ids(evidence: list[dict[str, Any]], top_k: int = 2) -> list[str]:
    return [str(row.get("doc_id", row.get("para_id", ""))) for row in evidence[:top_k]]
