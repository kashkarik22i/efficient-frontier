"""Download dividend-adjusted monthly index prices using yfinance."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yfinance as yf


YAHOO_SYMBOLS = {
    "europe600": "^STOXX",
    "msci_world": "^990100-USD-STRD",
    "sp500": "^GSPC",
}


def fetch_monthly_prices(symbol: str) -> pd.DataFrame:
    """Fetch daily adjusted prices and derive one closing value per month."""
    history = yf.Ticker(symbol).history(
        period="max",
        interval="1d",
        auto_adjust=True,
        actions=False,
    )
    if history.empty or "Close" not in history:
        raise RuntimeError(f"Yahoo Finance returned no usable data for {symbol}.")

    prices = (
        history[["Close"]]
        .rename(columns={"Close": "Price"})
        .dropna()
        .resample("M")
        .last()
        .dropna()
    )
    if prices.empty:
        raise RuntimeError(f"Yahoo Finance returned no usable prices for {symbol}.")
    prices["Date"] = prices.index.strftime("%m/%Y")
    prices = prices.reset_index(drop=True)[["Date", "Price"]]
    return prices.drop_duplicates("Date", keep="last").reset_index(drop=True)


def download_all(output_dir: Path, symbols: dict[str, str]) -> list[Path]:
    """Download configured symbols and return the generated file paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded = {asset: fetch_monthly_prices(symbol) for asset, symbol in symbols.items()}
    outputs = []
    for asset, prices in downloaded.items():
        monthly_path = output_dir / f"{asset}_yahoo.csv"
        prices.to_csv(monthly_path, index=False)
        outputs.append(monthly_path)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    parser.add_argument(
        "--symbol",
        action="append",
        metavar="ASSET=YAHOO_SYMBOL",
        help="Override a symbol, for example --symbol msci_world=URTH.",
    )
    args = parser.parse_args()

    symbols = YAHOO_SYMBOLS.copy()
    for override in args.symbol or []:
        asset, separator, symbol = override.partition("=")
        if not separator or asset not in symbols or not symbol:
            parser.error(f"symbol must be ASSET=YAHOO_SYMBOL for one of {sorted(symbols)}")
        symbols[asset] = symbol

    for output in download_all(args.output_dir, symbols):
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
