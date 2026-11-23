"""Preprocess every raw CSV into the processed data directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.data_io import raw_files
from scripts.preprocess import preprocess_file


def preprocess_all(input_dir: Path, output_dir: Path) -> list[Path]:
    """Process all raw CSV files and return the generated paths."""
    outputs = []
    for input_path in raw_files(input_dir):
        output_path = output_dir / f"{input_path.stem}_price_changes.csv"
        outputs.append(preprocess_file(input_path, output_path))
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    for output in preprocess_all(args.input_dir, args.output_dir):
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
