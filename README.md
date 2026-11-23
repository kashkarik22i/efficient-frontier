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
clean file per input into `data/processed/`:

```bash
python3 -m scripts.preprocess_all
```

Example output names are `europe600_price_changes.csv`,
`msci_world_price_changes.csv`, and `sp500_price_changes.csv`.

## 2. Visualize original prices

This reads the original files directly and creates an exploratory chart in
`results/`:

```bash
python3 -m scripts.visualize_prices
```

The chart is for local analysis only; production visualization is outside this
repository.

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
long-only portfolios whose weights sum to 1, and calculates 100
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
