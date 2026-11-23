# efficient-frontier

Reusable scripts for processing monthly price series. The three source files
currently in `data/raw/` are kept as inputs:

- `europe600.csv`
- `msci_world.csv`
- `sp500.csv`

Each file must contain a `Date` column in `MM/YYYY` format and exactly one
price column.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

## 1. Preprocess all raw files

This calculates period-over-period percentage price changes and writes one
processed file per input into `data/processed/`. Each file contains `Date`,
`Price`, and `Price change`. The original and Yahoo versions of each index are
kept at their full historical ranges and put on a common scale. The earlier
series starts at 10,000; the later series is multiplied so its first price
matches the earlier series' price at that date. The first row of each file has
no preceding month, so its `Price change` is empty.

```bash
python3 -m scripts.preprocess_all
```

Example output names are `europe600_price_changes.csv` and
`europe600_yahoo_price_changes.csv`.

## 2. Visualize raw prices

This reads the raw price files and creates an exploratory chart in `results/`.
The default input directory is `data/raw/`:

```bash
python3 -m scripts.visualize_prices
```

The chart is for local analysis only; production visualization is outside this
repository.

## Download dividend-adjusted monthly Yahoo Finance inputs

To create Yahoo Finance versions alongside the original files, run:

```bash
python3 -m scripts.download_yahoo
```

This writes `europe600_yahoo.csv`, `msci_world_yahoo.csv`, and
`sp500_yahoo.csv` to `data/raw/`. The files use the same `Date,price` shape as
the original inputs, with one `MM/YYYY` observation per month. Prices are
derived from `yfinance`'s maximum daily history by taking the last trading-day
close in each month. This avoids Yahoo's shorter monthly-interval history
limit. Prices use `auto_adjust=True`, so distributions such as dividends are
reflected where Yahoo supplies those adjustments. The default Yahoo symbols
are `^STOXX`, `^990100-USD-STRD`, and `^GSPC`, respectively.
Yahoo's index coverage and symbol availability can change; a symbol can be
overridden without changing the script:

```bash
python3 -m scripts.download_yahoo \
  --symbol msci_world=URTH
```

## 3. Calculate monthly mean return and CAGR

This creates `results/monthly_return_metrics.csv`:

```bash
python3 -m scripts.calculate_metrics
```

The report contains the arithmetic mean of monthly percentage returns and the
annualized compound annual growth rate (CAGR). CAGR uses the first and last
prices and the number of monthly intervals:

`(last price / first price) ** (12 / number of monthly intervals) - 1`

All scripts accept `--input-dir` and the output-producing scripts accept
custom output paths, so the modules can be reused with another data directory.

## 4. Build covariance matrix and efficient frontier

This uses the overlapping monthly history of all raw files. It assumes
long-only portfolios whose weights sum to 1, and calculates 500
minimum-variance portfolios across the range of individual-asset mean monthly
returns:

```bash
python3 -m scripts.build_frontier
```

This writes:

- `results/covariance_matrix.csv` — sample covariance matrix of monthly returns
- `results/efficient_frontier.csv` — frontier points and their asset weights

Visualize the individual assets and frontier points with:

```bash
python3 -m scripts.visualize_frontier
```

This writes `results/efficient_frontier.png`. Both portfolio scripts accept
`--input-dir`; the builder also accepts `--output-dir` and `--points`.
