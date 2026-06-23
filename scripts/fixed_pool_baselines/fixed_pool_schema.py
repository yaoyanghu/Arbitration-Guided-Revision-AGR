from __future__ import annotations

from collections import Counter
from typing import Any


def query_id(row: dict[str, Any]) -> str:
    return str(row.get("query_id", row.get("id", row.get("qid", "")))).strip()


def question_text(row: dict[str, Any]) -> str:
    return str(row.get("query", row.get("question", row.get("original_question", "")))).strip()


def gold_answers(row: dict[str, Any]) -> list[str]:
    value = row.get("answers", row.get("answer", row.get("gold_answers", row.get("gold_answer"))))
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, dict):
        for key in ("text", "answers", "answer"):
            if key in value:
                return gold_answers({"answers": value[key]})
        return []
    output: list[str] = []
    for item in value:
        text = str(item).strip()
        if text and text not in output:
            output.append(text)
    return output


def predicted_answer(row: dict[str, Any]) -> str:
    for key in ("predicted_answer", "final_answer", "prediction", "answer"):
        if key in row and row[key] is not None:
            return str(row[key]).strip()
    return ""


def prediction_validation(rows: list[dict[str, Any]], expected_ids: set[str]) -> dict[str, Any]:
    ids = [query_id(row) for row in rows]
    counts = Counter(ids)
    duplicate_ids = sorted(key for key, count in counts.items() if key and count > 1)
    observed = {value for value in ids if value}
    empty_answer_ids = sorted(query_id(row) for row in rows if not predicted_answer(row))
    parse_failure_ids = sorted(
        query_id(row) for row in rows
        if bool(row.get("parsing_failure", False)) or str(row.get("parse_status", "")).lower() not in ("", "ok", "success")
    )
    return {
        "row_count": len(rows),
        "unique_query_id_count": len(observed),
        "blank_query_id_rows": sum(1 for value in ids if not value),
        "duplicate_query_ids": duplicate_ids,
        "duplicate_query_id_count": len(duplicate_ids),
        "missing_query_ids": sorted(expected_ids - observed),
        "missing_query_id_count": len(expected_ids - observed),
        "unexpected_query_ids": sorted(observed - expected_ids),
        "unexpected_query_id_count": len(observed - expected_ids),
        "empty_answer_ids": empty_answer_ids,
        "empty_answer_count": len(empty_answer_ids),
        "parse_failure_ids": parse_failure_ids,
        "parse_failure_count": len(parse_failure_ids),
        "complete": not duplicate_ids and observed == expected_ids and not any(not value for value in ids),
    }
