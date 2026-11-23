"""Visualize efficient-frontier points and individual assets."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

from scripts.portfolio import load_aligned_returns


def plot_frontier(
    input_dir: Path,
    frontier_path: Path,
    output_path: Path,
) -> Path:
    """Plot monthly volatility and return for assets and frontier portfolios."""
    returns = load_aligned_returns(input_dir)
    frontier = pd.read_csv(frontier_path)
    required = {"monthly_return", "monthly_volatility"}
    missing = required.difference(frontier.columns)
    if missing:
        raise ValueError(f"Frontier data is missing columns: {', '.join(sorted(missing))}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(10, 6))
    asset_volatility = returns.std()
    asset_return = returns.mean()
    axis.scatter(asset_volatility, asset_return, label="Individual assets", zorder=3)
    for asset in returns.columns:
        axis.annotate(asset, (asset_volatility[asset], asset_return[asset]))
    axis.plot(
        frontier["monthly_volatility"],
        frontier["monthly_return"],
        label="Efficient frontier",
        color="black",
    )
    axis.scatter(
        frontier["monthly_volatility"],
        frontier["monthly_return"],
        color="black",
        s=10,
        zorder=2,
    )
    axis.set(
        title="Efficient frontier",
        xlabel="Monthly volatility",
        ylabel="Monthly expected return",
    )
    axis.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw"))
    parser.add_argument(
        "--frontier",
        type=Path,
        default=Path("results/efficient_frontier.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/efficient_frontier.png"),
    )
    args = parser.parse_args()
    print(f"Wrote {plot_frontier(args.input_dir, args.frontier, args.output)}")


if __name__ == "__main__":
    main()
