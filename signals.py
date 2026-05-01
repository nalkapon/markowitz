"""
Momentum signal: 12-month rolling momentum score (past cumulative return).
Used as expected return proxy in the Markowitz model.
"""

import pandas as pd
import numpy as np
import config


def momentum_scores(prices, lookback_months=None):
    """
    For each date t, compute past lookback_months cumulative log-return for each asset.
    Returns a DataFrame same index as prices (after warmup), columns = assets.
    """
    lookback_months = lookback_months or config.MOMENTUM_LOOKBACK_MONTHS
    # Approximate 21 trading days per month
    lookback_days = int(lookback_months * 21)

    log_ret = np.log(prices / prices.shift(1))
    # Rolling sum of log returns = log(P_t / P_{t-lookback})
    momentum = log_ret.rolling(window=lookback_days, min_periods=1).sum()
    # Drop warmup period where we don't have full lookback
    momentum = momentum.iloc[lookback_days:]
    return momentum


def momentum_scores_from_returns(returns, lookback_months=None):
    """
    Same as momentum_scores but from a returns DataFrame (e.g. log returns).
    """
    lookback_months = lookback_months or config.MOMENTUM_LOOKBACK_MONTHS
    lookback_days = int(lookback_months * 21)
    momentum = returns.rolling(window=lookback_days, min_periods=1).sum()
    momentum = momentum.iloc[lookback_days:]
    return momentum


def normalize_cross_sectional(scores):
    """
    Cross-sectional z-score normalization for each date.
    Produces expected return proxies comparable across assets.
    """
    def _zscore_row(row):
        std = row.std(ddof=0)
        if std is None or std == 0 or np.isnan(std):
            return pd.Series(0.0, index=row.index)
        out = (row - row.mean()) / std
        return out.fillna(0.0)

    normalized = scores.apply(_zscore_row, axis=1)
    return normalized
