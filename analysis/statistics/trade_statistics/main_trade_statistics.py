import pandas as pd

from analysis.statistics.trade_statistics.performance_metrics import performance_summary
from analysis.statistics.trade_statistics.risk_metrics import risk_summary
from analysis.statistics.trade_statistics.robustness_metrics import robustness_summary


def add_trade_statistics(trades, tick_value, commission):

    trades = calculate_net_trade_profit(trades, tick_value, commission)

    long_trades = filter_by_direction(trades, "long")
    short_trades = filter_by_direction(trades, "short")

    performance = performance_summary(trades, long_trades, short_trades)
    risk = risk_summary(trades)
    robustness = robustness_summary(trades, long_trades, short_trades)

    statistics = {}

    statistics.update(performance)
    statistics.update(risk)
    statistics.update(robustness)

    return statistics


def calculate_statistics_by_window(trades, tick_value, commission):

    if trades.empty:
        return pd.DataFrame()

    results = []

    grouped_trades = trades.groupby("window_id")

    for window_id, window_trades in grouped_trades:

        statistics = add_trade_statistics(window_trades, tick_value, commission)

        statistics["window_id"] = window_id

        results.append(statistics)

    results_df = pd.DataFrame(results)

    return results_df.sort_values("window_id").reset_index(drop=True)


def calculate_net_trade_profit(trades, tick_value, commission):

    df = trades.copy()

    if df.empty:
        df["net_trade_profit"] = []
        return df

    df["net_trade_profit"] = df["result"] * tick_value - commission

    return df


def filter_by_direction(trades, direction):

    if trades.empty:
        return trades

    return trades[trades["direction"] == direction]