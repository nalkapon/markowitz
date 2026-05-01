"""
Configuration for Multi-Sector Momentum Strategy (Stock Tigers - YAP 471).
"""

# Asset universe: 10 US Large-Cap equities across sectors
TICKERS = [
    "AAPL",   # Technology
    "JNJ",    # Healthcare
    "XOM",    # Energy
    "PG",     # Consumer Staples
    "JPM",    # Financials
    "NEE",    # Utilities
    "LMT",    # Industrials
    "GOLD",   # Materials
    "AMT",    # Real Estate
    "VZ",     # Communication
]

# Sample period: Jan 2021 - Jan 2026 (5 years)
START_DATE = "2021-01-01"
END_DATE = "2026-01-31"

# Momentum signal: 12-month lookback
MOMENTUM_LOOKBACK_MONTHS = 12

# Rolling window for covariance / rebalance (e.g. monthly)
ROLLING_WINDOW_DAYS = 252  # ~1 year for covariance estimation
COVARIANCE_MODE = "expanding"  # "expanding" or "rolling"

# Out-of-sample: e.g. last 2 years for testing (no look-ahead bias)
OOS_START_RATIO = 0.6  # first 60% train, last 40% test (or set OOS_START_DATE)
# Alternatively set explicit date:
OOS_START_DATE = None  # e.g. "2024-01-01" to override ratio

# Risk-free rate (annualized) for Sharpe ratio
RISK_FREE_RATE_ANNUAL = 0.05

# Volatility targeting (annualized)
VOL_TARGETING_ENABLED = True
VOL_TARGET_ANNUAL = 0.18

# Baseline fairness: compare strategy to monthly-rebalanced 1/N baseline
BASELINE_REBALANCE_FREQ = "monthly"  # "monthly" or "daily"

# Realism: transaction costs (one-way, in basis points) applied on turnover at rebalance
TRANSACTION_COST_BPS = 0.0
