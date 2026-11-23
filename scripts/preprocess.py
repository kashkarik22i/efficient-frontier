"""Transform one price series into percentage price changes."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.data_io import load_price_series


def price_changes(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate period-over-period percentage changes, retaining the first price."""
    changes = prices.copy()
    changes["Price change"] = changes["Price"].pct_change()
    return changes.reset_index(drop=True)


def align_pair(original: pd.DataFrame, yahoo: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Put an original/Yahoo pair on one scale without trimming either series."""
    original = original.copy()
    yahoo = yahoo.copy()
    original_start = original["Date"].min()
    yahoo_start = yahoo["Date"].min()

    if original_start <= yahoo_start:
        earlier, later = original, yahoo
    else:
        earlier, later = yahoo, original

    earlier["Price"] *= 10_000 / earlier.iloc[0]["Price"]
    later_start = later.iloc[0]["Date"]
    earlier_at_later_start = earlier[earlier["Date"] >= later_start]
    if earlier_at_later_start.empty:
        raise ValueError("Original and Yahoo series have no overlapping dates.")
    scale = (
        earlier_at_later_start.iloc[0]["Price"] / later.iloc[0]["Price"]
    )
    later["Price"] *= scale

    if original_start <= yahoo_start:
        return earlier, later
    return later, earlier


def preprocess_file(input_path: Path, output_path: Path) -> Path:
    """Read one raw file and write its processed price changes."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    price_changes(load_price_series(input_path)).to_csv(output_path, index=False)
    return output_path
