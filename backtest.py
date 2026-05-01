"""
Backtest: rolling rebalance using momentum + Markowitz weights.
Strictly in-sample until oos_start; then out-of-sample with no look-ahead.
Compares strategy vs equal-weight (1/N) baseline; reports Sharpe ratio.
"""

import pandas as pd
import numpy as np
from data import fetch_prices, get_returns_train_test
from signals import momentum_scores_from_returns, normalize_cross_sectional
from markowitz import markowitz_weights_from_returns, equal_weight
import config


def max_drawdown(log_return_series):
    equity = np.exp(log_return_series.cumsum())
    running_peak = equity.cummax()
    drawdown = equity / running_peak - 1.0
    return float(drawdown.min())


def cumulative_return(log_return_series):
    return float(np.exp(log_return_series.sum()) - 1.0)


def annualized_volatility(log_return_series, periods_per_year=252):
    return float(log_return_series.std() * np.sqrt(periods_per_year))


def apply_volatility_targeting(weights, cov, target_annual_vol, periods_per_year=252):
    pred_vol = float(np.sqrt(np.dot(weights, np.dot(cov, weights))) * np.sqrt(periods_per_year))
    if pred_vol <= 0 or pred_vol <= target_annual_vol:
        return weights

    adjusted = weights.copy()
    asset_vol = np.sqrt(np.maximum(np.diag(cov), 1e-12)) * np.sqrt(periods_per_year)
    inv_vol = 1.0 / np.maximum(asset_vol, 1e-8)
    inv_vol = inv_vol / inv_vol.sum()

    excess_ratio = (pred_vol - target_annual_vol) / pred_vol
    blend = float(np.clip(excess_ratio, 0.0, 1.0))
    adjusted = (1.0 - blend) * adjusted + blend * inv_vol
    adjusted = np.clip(adjusted, 0.0, 1.0)
    if adjusted.sum() <= 0:
        return weights
    adjusted = adjusted / adjusted.sum()
    return adjusted


def simulate_equal_weight_baseline(
    returns,
    oos_dates,
    rebalance_dates,
    rebalance_freq="monthly",
    transaction_cost_bps=0.0,
):
    """
    Fair baseline simulation in simple-return space with weight drift between rebalances.
    Returns daily log-return series aligned on oos_dates.
    """
    assets = returns.columns.tolist()
    n_assets = len(assets)
    target_w = np.ones(n_assets) / n_assets
    current_w = target_w.copy()

    baseline_log_rets = pd.Series(index=oos_dates, dtype=float)
    rebalance_set = set(pd.DatetimeIndex(rebalance_dates))
    tc_rate = transaction_cost_bps / 10000.0

    for idx, d in enumerate(oos_dates):
        d = pd.Timestamp(d)
        cost = 0.0

        if rebalance_freq == "daily" or (rebalance_freq == "monthly" and d in rebalance_set):
            if idx > 0:
                turnover = float(np.abs(target_w - current_w).sum())
                cost = turnover * tc_rate
            current_w = target_w.copy()

        simple_r = np.exp(np.nan_to_num(returns.loc[d].values, nan=0.0)) - 1.0
        port_simple = float(np.dot(current_w, simple_r))
        net_simple = port_simple - cost
        net_simple = max(net_simple, -0.999999)
        baseline_log_rets.loc[d] = np.log1p(net_simple)

        gross_growth = current_w * (1.0 + simple_r)
        gross_sum = gross_growth.sum()
        if gross_sum > 0:
            current_w = gross_growth / gross_sum

    return baseline_log_rets.dropna()


def backtest(
    returns,
    oos_start,
    rebalance_freq="monthly",
    rolling_cov_days=None,
    risk_aversion=1.0,
    covariance_mode=None,
    vol_targeting_enabled=None,
    vol_target_annual=None,
    transaction_cost_bps=None,
    baseline_rebalance_freq=None,
):
    """
    returns: DataFrame index=date, columns=assets.
    oos_start: first date of out-of-sample period (we only evaluate OOS).
    rebalance_freq: 'daily' or 'monthly'.
    rolling_cov_days: window for covariance estimation (default from config).
    Returns: (strategy_rets_oos, equal_weight_daily_rets_oos, equal_weight_fair_rets_oos, rebalance_dates).
    """
    rolling_cov_days = rolling_cov_days or config.ROLLING_WINDOW_DAYS
    covariance_mode = covariance_mode or config.COVARIANCE_MODE
    vol_targeting_enabled = (
        config.VOL_TARGETING_ENABLED if vol_targeting_enabled is None else vol_targeting_enabled
    )
    vol_target_annual = vol_target_annual or config.VOL_TARGET_ANNUAL
    transaction_cost_bps = config.TRANSACTION_COST_BPS if transaction_cost_bps is None else transaction_cost_bps
    baseline_rebalance_freq = baseline_rebalance_freq or config.BASELINE_REBALANCE_FREQ
    assets = returns.columns.tolist()
    n_assets = len(assets)

    momentum = momentum_scores_from_returns(returns)
    momentum = normalize_cross_sectional(momentum)

    # Align: only consider dates where we have momentum
    common = returns.index.intersection(momentum.index)
    returns = returns.reindex(common).dropna(how="all")
    momentum = momentum.reindex(common).ffill().dropna(how="all")
    common = returns.index.intersection(momentum.index)

    # Rebalance dates (OOS only): we compute weights on these dates and hold until next
    oos_dates = common[common >= oos_start]
    if oos_dates.empty:
        raise ValueError("No OOS dates after oos_start")

    if rebalance_freq == "monthly":
        # First trading day of each month in OOS
        df_rb = pd.DataFrame({"date": oos_dates}, index=oos_dates)
        df_rb["ym"] = df_rb["date"].dt.to_period("M")
        first_per_month = df_rb.groupby("ym")["date"].first()
        rebalance_dates = pd.DatetimeIndex(first_per_month.values)
    else:
        rebalance_dates = pd.DatetimeIndex(oos_dates.values)

    # Build daily strategy returns (OOS only): one return per day
    strat_rets = pd.Series(index=oos_dates, dtype=float)
    eq_rets = pd.Series(index=oos_dates, dtype=float)

    # Precompute weights at each rebalance date (no look-ahead: only data before rb_d)
    weights_at_rb = {}
    for rb_d in rebalance_dates:
        past = returns.loc[returns.index < rb_d]
        if len(past) < rolling_cov_days:
            weights_at_rb[rb_d] = equal_weight(n_assets)
        else:
            if covariance_mode == "expanding":
                past_window = past
            else:
                past_window = past.iloc[-rolling_cov_days:]
            last_date = past.index[-1]
            mu_proxy = momentum.loc[last_date].values if last_date in momentum.index else np.zeros(n_assets)
            mu_proxy = np.nan_to_num(mu_proxy, nan=0.0)
            weights = markowitz_weights_from_returns(
                past_window, mu_proxy, risk_aversion=risk_aversion
            )
            if vol_targeting_enabled:
                cov = np.cov(np.asarray(past_window).T)
                cov = np.maximum(cov, cov.T)
                weights = apply_volatility_targeting(
                    weights,
                    cov,
                    target_annual_vol=vol_target_annual,
                )
            weights_at_rb[rb_d] = weights

    # For each OOS day, use last rebalance weight and compute portfolio return
    current_w = equal_weight(n_assets)
    prev_w = current_w.copy()
    tc_rate = transaction_cost_bps / 10000.0
    for d in oos_dates:
        d = pd.Timestamp(d)
        cost = 0.0
        if d in rebalance_dates:
            current_w = weights_at_rb[d]
            turnover = float(np.abs(current_w - prev_w).sum())
            cost = turnover * tc_rate
            prev_w = current_w.copy()
        if d in returns.index:
            r = np.nan_to_num(returns.loc[d].values, nan=0.0)
            strat_rets.loc[d] = np.dot(current_w, r) - cost
            eq_rets.loc[d] = np.mean(r)
        else:
            strat_rets.loc[d] = np.nan
            eq_rets.loc[d] = np.nan

    strat_rets = strat_rets.dropna()
    eq_rets = eq_rets.reindex(strat_rets.index).fillna(0)
    eq_fair_rets = simulate_equal_weight_baseline(
        returns=returns,
        oos_dates=strat_rets.index,
        rebalance_dates=rebalance_dates,
        rebalance_freq=baseline_rebalance_freq,
        transaction_cost_bps=transaction_cost_bps,
    )
    eq_fair_rets = eq_fair_rets.reindex(strat_rets.index).fillna(0)
    return strat_rets, eq_rets, eq_fair_rets, rebalance_dates


def sharpe_ratio(series, risk_free_annual=None, periods_per_year=252):
    """Annualized Sharpe ratio (excess return / vol)."""
    risk_free_annual = risk_free_annual or config.RISK_FREE_RATE_ANNUAL
    rf_per_period = risk_free_annual / periods_per_year
    excess = series - rf_per_period
    if excess.std() == 0:
        return 0.0
    return np.sqrt(periods_per_year) * excess.mean() / excess.std()


def run_full_backtest(
    rebalance_freq="monthly",
    risk_aversion=1.0,
    winsorize_std=5.0,
    covariance_mode=None,
    vol_targeting_enabled=None,
    vol_target_annual=None,
    transaction_cost_bps=None,
    baseline_rebalance_freq=None,
):
    """
    Fetch data, split train/OOS, run backtest, print metrics.
    """
    print("Fetching prices...")
    prices = fetch_prices()
    returns, train_end, oos_start = get_returns_train_test(
        prices, winsorize_std=winsorize_std
    )
    print(f"Train until: {train_end}, OOS from: {oos_start}")
    print("Running backtest (OOS only)...")
    strat_rets, eq_rets, eq_fair_rets, _ = backtest(
        returns,
        oos_start,
        rebalance_freq=rebalance_freq,
        risk_aversion=risk_aversion,
        covariance_mode=covariance_mode,
        vol_targeting_enabled=vol_targeting_enabled,
        vol_target_annual=vol_target_annual,
        transaction_cost_bps=transaction_cost_bps,
        baseline_rebalance_freq=baseline_rebalance_freq,
    )

    sharpe_strat = sharpe_ratio(strat_rets)
    sharpe_eq = sharpe_ratio(eq_rets)
    sharpe_eq_fair = sharpe_ratio(eq_fair_rets)
    ann_ret_strat = strat_rets.mean() * 252
    ann_ret_eq = eq_rets.mean() * 252
    ann_ret_eq_fair = eq_fair_rets.mean() * 252
    vol_strat = annualized_volatility(strat_rets)
    vol_eq = annualized_volatility(eq_rets)
    vol_eq_fair = annualized_volatility(eq_fair_rets)
    cumret_strat = cumulative_return(strat_rets)
    cumret_eq = cumulative_return(eq_rets)
    cumret_eq_fair = cumulative_return(eq_fair_rets)
    maxdd_strat = max_drawdown(strat_rets)
    maxdd_eq = max_drawdown(eq_rets)
    maxdd_eq_fair = max_drawdown(eq_fair_rets)

    print("\n--- Out-of-Sample Results ---")
    print(f"Covariance mode: {covariance_mode or config.COVARIANCE_MODE}")
    print(
        f"Vol targeting: {'ON' if (config.VOL_TARGETING_ENABLED if vol_targeting_enabled is None else vol_targeting_enabled) else 'OFF'}"
        f" (target={vol_target_annual or config.VOL_TARGET_ANNUAL:.2%})"
    )
    print(f"Transaction cost: {(config.TRANSACTION_COST_BPS if transaction_cost_bps is None else transaction_cost_bps):.2f} bps")
    print(f"Fair baseline rebalance: {baseline_rebalance_freq or config.BASELINE_REBALANCE_FREQ}")
    print(f"Strategy (Momentum + Markowitz)  Sharpe: {sharpe_strat:.4f}  Ann.Ret: {ann_ret_strat:.4f}  Vol: {vol_strat:.4f}  CumRet: {cumret_strat:.4f}  MaxDD: {maxdd_strat:.4f}")
    print(f"Equal-weight (1/N) baseline     Sharpe: {sharpe_eq:.4f}  Ann.Ret: {ann_ret_eq:.4f}  Vol: {vol_eq:.4f}  CumRet: {cumret_eq:.4f}  MaxDD: {maxdd_eq:.4f}")
    print(f"Equal-weight (1/N, fair)        Sharpe: {sharpe_eq_fair:.4f}  Ann.Ret: {ann_ret_eq_fair:.4f}  Vol: {vol_eq_fair:.4f}  CumRet: {cumret_eq_fair:.4f}  MaxDD: {maxdd_eq_fair:.4f}")
    print(f"Sharpe improvement: {sharpe_strat - sharpe_eq:+.4f}")
    print(f"Sharpe improvement (fair): {sharpe_strat - sharpe_eq_fair:+.4f}")
    return {
        "strategy_rets": strat_rets,
        "equal_weight_rets": eq_rets,
        "equal_weight_fair_rets": eq_fair_rets,
        "sharpe_strategy": sharpe_strat,
        "sharpe_equal_weight": sharpe_eq,
        "sharpe_equal_weight_fair": sharpe_eq_fair,
        "cumret_strategy": cumret_strat,
        "cumret_equal_weight": cumret_eq,
        "cumret_equal_weight_fair": cumret_eq_fair,
        "maxdd_strategy": maxdd_strat,
        "maxdd_equal_weight": maxdd_eq,
        "maxdd_equal_weight_fair": maxdd_eq_fair,
        "prices": prices,
        "returns": returns,
        "oos_start": oos_start,
    }
