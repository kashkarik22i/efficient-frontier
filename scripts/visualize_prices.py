"""Plot prices from all original raw files for local exploration."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

from scripts.data_io import asset_name, load_price_series, raw_files


def plot_prices(input_dir: Path, output_path: Path) -> Path:
    """Create one chart containing every raw price series."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(11, 6))
    for input_path in raw_files(input_dir):
        prices = load_price_series(input_path)
        axis.plot(prices["Date"], prices["Price"], label=asset_name(input_path))
    axis.set(title="Original price series", xlabel="Date", ylabel="Price")
    axis.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
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
        "--output",
        type=Path,
        default=Path("results/original_prices.png"),
    )
    args = parser.parse_args()
    print(f"Wrote {plot_prices(args.input_dir, args.output)}")


if __name__ == "__main__":
    main()
