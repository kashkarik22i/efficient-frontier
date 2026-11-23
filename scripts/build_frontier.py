"""Build a covariance matrix and efficient-frontier points."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.portfolio import covariance_matrix, efficient_frontier, load_aligned_returns


def build_outputs(input_dir: Path, output_dir: Path, points: int = 500) -> list[Path]:
    """Calculate and write portfolio-analysis outputs."""
    returns = load_aligned_returns(input_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    covariance_path = output_dir / "covariance_matrix.csv"
    frontier_path = output_dir / "efficient_frontier.csv"
    covariance_matrix(returns).to_csv(covariance_path)
    efficient_frontier(returns, points=points).to_csv(frontier_path, index=False)
    return [covariance_path, frontier_path]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--points", type=int, default=500)
    args = parser.parse_args()
    for output in build_outputs(args.input_dir, args.output_dir, args.points):
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
