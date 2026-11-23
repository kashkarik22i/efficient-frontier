"""Reusable portfolio calculations for monthly price series."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from scripts.data_io import asset_name, load_price_series, raw_files


def load_aligned_returns(input_dir: Path) -> pd.DataFrame:
    """Load all raw price files and return returns on shared dates."""
    series = []
    for path in raw_files(input_dir):
        prices = load_price_series(path).set_index("Date")["Price"]
        series.append(prices.rename(asset_name(path)))
    prices = pd.concat(series, axis=1, join="inner").dropna()
    if len(prices) < 2:
        raise ValueError("The price files do not contain at least two shared dates.")
    returns = prices.pct_change().dropna()
    if returns.empty:
        raise ValueError("The shared price history does not produce any returns.")
    return returns


def covariance_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Calculate the sample covariance matrix of monthly returns."""
    return returns.cov()


def _portfolio_return(weights: np.ndarray, expected_returns: np.ndarray) -> float:
    return float(weights @ expected_returns)


def _portfolio_volatility(weights: np.ndarray, covariance: np.ndarray) -> float:
    variance = float(weights @ covariance @ weights)
    return float(np.sqrt(max(variance, 0.0)))


def efficient_frontier(
    returns: pd.DataFrame,
    points: int = 100,
) -> pd.DataFrame:
    """Calculate long-only, fully invested minimum-variance frontier points."""
    if points < 2:
        raise ValueError("At least two frontier points are required.")

    expected = returns.mean().to_numpy()
    covariance = returns.cov().to_numpy()
    assets = returns.columns.tolist()
    initial = np.full(len(assets), 1 / len(assets))
    bounds = [(0.0, 1.0)] * len(assets)
    targets = np.linspace(expected.min(), expected.max(), points)
    rows = []

    for target in targets:
        constraints = [
            {"type": "eq", "fun": lambda weights: weights.sum() - 1},
            {
                "type": "eq",
                "fun": lambda weights, target=target: weights @ expected - target,
            },
        ]
        result = minimize(
            lambda weights: weights @ covariance @ weights,
            initial,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"ftol": 1e-12, "maxiter": 1_000},
        )
        if not result.success:
            raise RuntimeError(f"Frontier optimization failed at target {target}: {result.message}")

        weights = result.x
        rows.append(
            {
                "target_monthly_return": target,
                "monthly_return": _portfolio_return(weights, expected),
                "monthly_volatility": _portfolio_volatility(weights, covariance),
                **{f"weight_{asset}": weight for asset, weight in zip(assets, weights)},
            }
        )
        initial = weights

    frontier = pd.DataFrame(rows)
    minimum_volatility = frontier["monthly_volatility"].idxmin()
    return frontier.loc[minimum_volatility:].reset_index(drop=True)
