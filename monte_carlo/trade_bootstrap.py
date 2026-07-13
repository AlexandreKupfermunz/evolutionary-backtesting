import numpy as np

def trade_bootstrap(trades_results, random_seed=10):

    trade_results = np.asarray(trades_results, dtype=float)

    if trade_results.ndim != 1:
        raise ValueError("results must be a one-dimensional array.")

    if not np.all(np.isfinite(trade_results)):
        raise ValueError("results must contain only finite numeric values.")
    
    if len(trades_results)==0:
        raise ValueError("trade_results must contain trades")

    rng = np.random.default_rng(random_seed)

    number_of_trades = len(trades_results)


    indexes = rng.integers(number_of_trades, size = (number_of_trades,))

    bootstrap = trades_results[indexes]

    return bootstrap