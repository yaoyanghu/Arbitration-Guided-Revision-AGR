from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dense vector index.")
    parser.add_argument("--corpus-dir", default="corpus/wiki2018")
    parser.add_argument("--index-dir", default="indexes/dense")
    args = parser.parse_args()
    print(f"[TODO] Build dense index from {args.corpus_dir} into {args.index_dir}")


if __name__ == "__main__":
    main()
