from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ChronoRAG attribution evaluation.")
    parser.add_argument("--route", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    print(f"[INFO] Route: {args.route}")
    print(f"[INFO] Config: {Path(args.config).resolve()}")
    print("[TODO] Add citation accuracy and unsupported span evaluation here.")


if __name__ == "__main__":
    main()
