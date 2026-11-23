"""Transform one price series into percentage price changes."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.data_io import load_price_series


def price_changes(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate period-over-period percentage changes."""
    changes = prices.copy()
    changes["Price change"] = changes["Price"].pct_change()
    return changes.dropna().reset_index(drop=True)


def preprocess_file(input_path: Path, output_path: Path) -> Path:
    """Read one raw file and write its processed price changes."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    price_changes(load_price_series(input_path)).to_csv(output_path, index=False)
    return output_path
