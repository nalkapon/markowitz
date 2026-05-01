"""
Markowitz allocator: maximize mu'w - (lambda/2) w'Sigma w
subject to 0 <= w <= 1 (no short), sum(w) = 1 (budget).
Uses momentum scores as expected return proxy (mu).
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize

import config


def _markowitz_weights(mu, cov, risk_aversion=1.0):
    """
    Solve for optimal weights: max mu'w - (risk_aversion/2) * w' cov w
    s.t. sum(w)=1, 0 <= w <= 1.
    mu, cov: numpy arrays (1d, 2d). cov must be PSD.
    """
    n = len(mu)
    # Objective: negative (minimize negative = maximize)
    def neg_utility(w):
        return -(np.dot(mu, w) - 0.5 * risk_aversion * np.dot(w, np.dot(cov, w)))

    # Constraints: sum(w)=1
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = [(0.0, 1.0)] * n
    x0 = np.ones(n) / n

    res = minimize(neg_utility, x0, method="SLSQP", bounds=bounds, constraints=constraints)
    if not res.success:
        # Fallback: equal weight
        return np.ones(n) / n
    return res.x


def markowitz_weights_from_returns(returns_window, mu_proxy, risk_aversion=1.0):
    """
    Covariance from returns_window (e.g. last 252 days), expected return from mu_proxy (momentum).
    returns_window: DataFrame or 2d array, rows = time, cols = assets.
    mu_proxy: 1d array, same length as assets (e.g. last row of momentum for current date).
    """
    if hasattr(returns_window, "values"):
        R = returns_window.values
    else:
        R = np.asarray(returns_window)
    R = np.atleast_2d(R)
    if R.shape[0] < 2:
        n = R.shape[1]
        return np.ones(n) / n

    cov = np.cov(R.T)
    # Ensure PSD (numerical)
    cov = np.maximum(cov, cov.T)
    eigvals = np.linalg.eigvalsh(cov)
    if eigvals.min() < 1e-10:
        cov += (1e-8 - eigvals.min()) * np.eye(cov.shape[0])

    mu = np.asarray(mu_proxy).ravel()
    if len(mu) != R.shape[1]:
        n = R.shape[1]
        return np.ones(n) / n
    return _markowitz_weights(mu, cov, risk_aversion=risk_aversion)


def equal_weight(n):
    return np.ones(n) / n
