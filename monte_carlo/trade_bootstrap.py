import numpy as np

def trade_bootstrap(trades_results_np, random_seed=10):

    rng = np.random.default_rng(random_seed)

    if len(trades_results_np)==0:
        raise ValueError

    number_of_trades = len(trades_results_np)

    if trades_results_np.shape != (number_of_trades,):
        raise ValueError

    indexes = rng.integers(number_of_trades, size = (number_of_trades,))

    bootstrap = trades_results_np[indexes]

    return bootstrap