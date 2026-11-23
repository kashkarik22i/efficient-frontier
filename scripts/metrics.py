"""Return metrics for monthly price series."""

from __future__ import annotations

import pandas as pd


def calculate_metrics(prices: pd.DataFrame) -> dict[str, float | int | str]:
    """Calculate arithmetic mean monthly return and annualized CAGR."""
    returns = prices["Price"].pct_change().dropna()
    periods = len(returns)
    if periods == 0:
        raise ValueError("At least two prices are required to calculate metrics.")

    cagr = (prices["Price"].iloc[-1] / prices["Price"].iloc[0]) ** (12 / periods) - 1
    return {
        "arithmetic_mean_monthly_return": returns.mean(),
        "cagr": cagr,
        "observations": periods,
        "start_date": prices["Date"].iloc[0].strftime("%Y-%m-%d"),
        "end_date": prices["Date"].iloc[-1].strftime("%Y-%m-%d"),
    }
