from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate final answer with citations.")
    parser.add_argument("--input", default="outputs/final_evidence.jsonl")
    args = parser.parse_args()
    print(f"[TODO] Generate answer using {args.input}")


if __name__ == "__main__":
    main()
