from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Build lightweight evidence graph.")
    parser.add_argument("--input", default="outputs/reranked_candidates.jsonl")
    args = parser.parse_args()
    print(f"[TODO] Build evidence graph from {args.input}")


if __name__ == "__main__":
    main()
