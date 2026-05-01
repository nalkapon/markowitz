"""
Data module: fetch prices from Yahoo Finance, clean data, enforce train/test split.
Avoids look-ahead bias by strict separation of in-sample and out-of-sample periods.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import time

try:
    import yfinance as yf
except ImportError:
    raise ImportError("Install yfinance: pip install yfinance")

import config


def _extract_close_from_raw(raw, tickers):
    """Normalize yfinance output into a close-price DataFrame with ticker columns."""
    if raw is None or raw.empty:
        return pd.DataFrame(columns=tickers)

    if isinstance(raw.columns, pd.MultiIndex):
        close_col = "Close" if any(c[1] == "Close" for c in raw.columns) else "Adj Close"
        close = pd.DataFrame(
            {t: raw[(t, close_col)] for t in tickers if (t, close_col) in raw.columns}
        )
    else:
        col = "Close" if "Close" in raw.columns else "Adj Close"
        if len(tickers) == 1:
            close = raw[col].to_frame(tickers[0])
        else:
            close = raw[col].copy()
            if isinstance(close, pd.Series):
                close = close.to_frame(tickers[0])

    return close.reindex(columns=tickers)


def fetch_prices(tickers=None, start=None, end=None):
    """
    Download daily adjusted closing prices from Yahoo Finance.
    Handles non-trading days: calendar is aligned, missing days filled with NaN then ffill.
    """
    tickers = tickers or config.TICKERS
    start = start or config.START_DATE
    end = end or config.END_DATE

    close = pd.DataFrame(columns=tickers)

    # 1) Try fast batched download first (short timeout, no threads to reduce lockups on some machines)
    last_error = None
    for _ in range(2):
        try:
            raw = yf.download(
                tickers,
                start=start,
                end=end,
                progress=False,
                auto_adjust=True,
                group_by="ticker",
                threads=False,
                timeout=15,
            )
            close = _extract_close_from_raw(raw, tickers)
            if not close.empty and close.notna().any().any():
                break
        except Exception as exc:
            last_error = exc
            time.sleep(0.5)

    # 2) Fallback: download each ticker separately so one bad request doesn't block all
    if close.empty or not close.notna().any().any():
        parts = []
        for t in tickers:
            try:
                raw_t = yf.download(
                    t,
                    start=start,
                    end=end,
                    progress=False,
                    auto_adjust=True,
                    threads=False,
                    timeout=15,
                )
                c = _extract_close_from_raw(raw_t, [t])
                if not c.empty:
                    parts.append(c)
            except Exception:
                continue

        if parts:
            close = pd.concat(parts, axis=1)
            close = close.reindex(columns=tickers)

    if close.empty or not close.notna().any().any():
        if last_error is not None:
            raise RuntimeError(f"Yahoo Finance verisi indirilemedi: {last_error}")
        raise RuntimeError("Yahoo Finance verisi indirilemedi. İnternet bağlantısı veya geçici API sorunu olabilir.")

    # Forward-fill non-trading days (then drop leading NaN from warmup)
    close = close.ffill()
    close = close.dropna(how="all")
    return close


def clean_returns(prices, winsorize_std=5.0):
    """
    Compute log returns and optionally winsorize outliers.
    winsorize_std: cap at ± this many std (None to skip).
    """
    log_ret = np.log(prices / prices.shift(1)).dropna(how="all")
    if winsorize_std is not None and winsorize_std > 0:
        for c in log_ret.columns:
            s = log_ret[c]
            mu, std = s.mean(), s.std()
            if std > 0:
                log_ret[c] = s.clip(mu - winsorize_std * std, mu + winsorize_std * std)
    return log_ret


def get_train_test_dates(prices, oos_start_ratio=None, oos_start_date=None):
    """
    Return (train_end_date, oos_start_date) so that:
    - Train: from start up to (but not including) oos_start_date.
    - Test (OOS): from oos_start_date to end.
    No look-ahead: OOS decisions use only data up to the decision time.
    """
    oos_start_ratio = oos_start_ratio if oos_start_ratio is not None else config.OOS_START_RATIO
    oos_start_date = oos_start_date or config.OOS_START_DATE

    if oos_start_date is not None:
        oos_dt = pd.Timestamp(oos_start_date)
    else:
        idx = prices.index
        n = len(idx)
        cut = int(n * oos_start_ratio)
        oos_dt = idx[cut]

    train_end = oos_dt - pd.Timedelta(days=1)
    return train_end, oos_dt


def get_returns_train_test(prices, winsorize_std=5.0, oos_start_ratio=None, oos_start_date=None):
    """
    Returns (returns_df, train_end_date, oos_start_date).
    returns_df is aligned daily; you slice by date for train vs OOS.
    """
    returns = clean_returns(prices, winsorize_std=winsorize_std)
    train_end, oos_start = get_train_test_dates(prices, oos_start_ratio, oos_start_date)
    return returns, train_end, oos_start
