"""Create a results report for every raw monthly price series."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.data_io import asset_name, load_price_series, raw_files
from scripts.metrics import calculate_metrics


def build_report(input_dir: Path, output_path: Path) -> Path:
    """Calculate metrics for all raw files and write one CSV report."""
    rows = []
    for input_path in raw_files(input_dir):
        row = {"asset": asset_name(input_path), **calculate_metrics(load_price_series(input_path))}
        rows.append(row)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/monthly_return_metrics.csv"),
    )
    args = parser.parse_args()
    print(f"Wrote {build_report(args.input_dir, args.output)}")


if __name__ == "__main__":
    main()
