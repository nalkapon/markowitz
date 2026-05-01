"""
YAP 471 - Stock Tigers: Multi-Sector Momentum Strategy with Markowitz Allocator.
Entry point: fetch data, run OOS backtest, report Sharpe vs equal-weight.
"""

from backtest import run_full_backtest


if __name__ == "__main__":
    results = run_full_backtest(
        rebalance_freq="monthly",
        risk_aversion=1.0,
        winsorize_std=5.0,
    )
    print("\nDone.")
