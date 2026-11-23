"""Shared input and output helpers for the data scripts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_price_series(path: Path) -> pd.DataFrame:
    """Load a monthly CSV with a date column and one price column."""
    data = pd.read_csv(path)
    date_column = next((column for column in data.columns if column.lower() == "date"), None)
    if date_column is None:
        raise ValueError(f"{path} must contain a 'Date' column.")

    price_columns = [column for column in data.columns if column != date_column]
    if len(price_columns) != 1:
        raise ValueError(f"{path} must contain exactly one price column.")

    price_column = price_columns[0]
    prices = pd.DataFrame(
        {
            "Date": pd.to_datetime(data[date_column], format="%m/%Y"),
            "Price": pd.to_numeric(data[price_column], errors="raise"),
        }
    ).sort_values("Date")
    if prices["Date"].duplicated().any():
        raise ValueError(f"{path} contains duplicate dates.")
    if prices["Price"].isna().any() or (prices["Price"] <= 0).any():
        raise ValueError(f"{path} contains missing or non-positive prices.")
    if len(prices) < 2:
        raise ValueError(f"{path} must contain at least two observations.")
    return prices.reset_index(drop=True)


def raw_files(input_dir: Path) -> list[Path]:
    """Return all CSV inputs in deterministic order."""
    files = sorted(input_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}.")
    return files


def processed_files(input_dir: Path) -> list[Path]:
    """Return all processed price-change CSVs in deterministic order."""
    files = sorted(input_dir.glob("*_price_changes.csv"))
    if not files:
        raise FileNotFoundError(f"No processed CSV files found in {input_dir}.")
    return files


def load_processed_price_series(path: Path) -> pd.DataFrame:
    """Load a processed CSV containing dates, prices, and price changes."""
    data = pd.read_csv(path)
    required_columns = {"Date", "Price"}
    if not required_columns.issubset(data.columns):
        raise ValueError(f"{path} must contain Date and Price columns.")
    prices = pd.DataFrame(
        {
            "Date": pd.to_datetime(data["Date"], errors="raise"),
            "Price": pd.to_numeric(data["Price"], errors="raise"),
        }
    ).sort_values("Date")
    if prices["Date"].duplicated().any():
        raise ValueError(f"{path} contains duplicate dates.")
    if prices["Price"].isna().any() or (prices["Price"] <= 0).any():
        raise ValueError(f"{path} contains missing or non-positive prices.")
    return prices.reset_index(drop=True)


def asset_name(path: Path) -> str:
    """Return the source file stem as a stable asset identifier."""
    return path.stem
