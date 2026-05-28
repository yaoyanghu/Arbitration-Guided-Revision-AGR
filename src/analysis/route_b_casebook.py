from __future__ import annotations

import argparse
from pathlib import Path

from src.common import read_json, read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Route B minimal prototype reports.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--report-dir", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    metrics = read_json(run_dir / "metrics.json")
    artifacts = read_jsonl(run_dir / "per_query_graph_artifacts.jsonl")

    improved = [item for item in artifacts if item.get("graph_preferred_rank") is not None and item.get("route_a_final_rank") is not None and item["graph_preferred_rank"] < item["route_a_final_rank"]]
    regressed = [item for item in artifacts if item.get("graph_preferred_rank") is not None and item.get("route_a_final_rank") is not None and item["graph_preferred_rank"] > item["route_a_final_rank"]]
    structured = [item for item in artifacts if int(item.get("edge_count", 0)) > 0]

    result_lines = [
        "# Route B Graph v1 Result Summary",
        "",
        "| stage | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        f"| route_a_final | {metrics['route_a_final']['preferred_top1_rate']:.3f} | {metrics['route_a_final']['pairwise_preference_success_rate']:.3f} | {metrics['route_a_final']['mean_preferred_rank']:.3f} | {metrics['route_a_final']['preferred_mrr']:.3f} | {metrics['route_a_final']['stale_wins_count']} |",
        f"| route_b_graph | {metrics['route_b_graph']['preferred_top1_rate']:.3f} | {metrics['route_b_graph']['pairwise_preference_success_rate']:.3f} | {metrics['route_b_graph']['mean_preferred_rank']:.3f} | {metrics['route_b_graph']['preferred_mrr']:.3f} | {metrics['route_b_graph']['stale_wins_count']} |",
        "",
        "## Graph Snapshot",
        "",
        f"- queries with nonempty graph: `{metrics['graph_snapshot']['queries_with_nonempty_graph']}`",
        f"- relation type counts: `{metrics['graph_snapshot']['relation_type_counts']}`",
        f"- improved count: `{metrics['graph_snapshot']['improved_count']}`",
        f"- regressed count: `{metrics['graph_snapshot']['regressed_count']}`",
        f"- no-change count: `{metrics['graph_snapshot']['no_change_count']}`",
    ]
    (report_dir / "RESULT_SUMMARY.md").write_text("\n".join(result_lines), encoding="utf-8")

    case_lines = ["# Route B Graph v1 Casebook", "", "## Improved Cases", ""]
    for item in improved[:5]:
        case_lines.append(f"- `{item['query_id']}`: Route A final `{item['route_a_final_rank']}` -> graph `{item['graph_preferred_rank']}`")
        case_lines.append(f"  query: {item['query']}")
        case_lines.append(f"  edge counts: {item['edge_type_counts']}")
    case_lines.extend(["", "## Regressed Cases", ""])
    for item in regressed[:5]:
        case_lines.append(f"- `{item['query_id']}`: Route A final `{item['route_a_final_rank']}` -> graph `{item['graph_preferred_rank']}`")
        case_lines.append(f"  query: {item['query']}")
        case_lines.append(f"  edge counts: {item['edge_type_counts']}")
    case_lines.extend(["", "## Relation Structure Examples", ""])
    for item in structured[:5]:
        case_lines.append(f"- `{item['query_id']}`: edge count `{item['edge_count']}`, edge counts `{item['edge_type_counts']}`")
        case_lines.append(f"  query: {item['query']}")
    (report_dir / "CASEBOOK.md").write_text("\n".join(case_lines), encoding="utf-8")

    a_top1 = metrics["route_a_final"]["preferred_top1_rate"]
    b_top1 = metrics["route_b_graph"]["preferred_top1_rate"]
    a_pairwise = metrics["route_a_final"]["pairwise_preference_success_rate"]
    b_pairwise = metrics["route_b_graph"]["pairwise_preference_success_rate"]
    empty_graph = metrics["graph_snapshot"]["queries_with_nonempty_graph"] == 0
    relation_structure = not empty_graph and len(metrics["graph_snapshot"]["relation_type_counts"]) >= 2
    net_gain = b_top1 > a_top1 or b_pairwise > a_pairwise

    if empty_graph:
        next_step = "暂停"
    elif net_gain:
        next_step = "继续扩成 prototype+"
    elif relation_structure:
        next_step = "降级为分析模块"
    else:
        next_step = "暂停"

    decision_lines = [
        "# Next Step Decision",
        "",
        f"- graph 是不是空壳: {'是' if empty_graph else '不是'}",
        f"- graph 是否形成了可解释的 relation structure: {'是' if relation_structure else '否'}",
        f"- A + graph aggregation 相比 A only 是否有净增益: {'是' if net_gain else '否'}",
        f"- Route B 下一步应当是: `{next_step}`",
    ]
    (report_dir / "NEXT_STEP_DECISION.md").write_text("\n".join(decision_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
