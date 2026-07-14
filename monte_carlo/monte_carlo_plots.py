from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_equity_curves(equity_curves, original_equity_curve, output_path, number_of_curves_to_plot=100, random_seed=10):

    equity_curves = np.asarray(equity_curves, dtype=float)
    original_equity_curve = np.asarray(original_equity_curve, dtype=float)

    if equity_curves.ndim != 2:
        raise ValueError("equity_curves must be a two-dimensional array.")

    if equity_curves.shape[0] == 0:
        raise ValueError("equity_curves must contain at least one simulation.")

    if equity_curves.shape[1] < 2:
        raise ValueError("Each equity curve must contain at least two points.")

    if not np.all(np.isfinite(equity_curves)):
        raise ValueError("equity_curves must contain only finite values.")

    if original_equity_curve.ndim != 1:
        raise ValueError("original_equity_curve must be a one-dimensional array.")

    if not np.all(np.isfinite(original_equity_curve)):
        raise ValueError("original_equity_curve must contain only finite values.")

    if equity_curves.shape[1] != original_equity_curve.size:
        raise ValueError("The simulated and original equity curves must have the same length.")

    if number_of_curves_to_plot <= 0:
        raise ValueError("number_of_curves_to_plot must be greater than zero.")

    number_of_simulations = equity_curves.shape[0]

    number_of_selected_curves = min(number_of_curves_to_plot, number_of_simulations)

    rng = np.random.default_rng(random_seed)

    selected_indexes = rng.choice(number_of_simulations, size=number_of_selected_curves, replace=False)

    trade_numbers = np.arange(equity_curves.shape[1])

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(12, 7))

    for simulation_index in selected_indexes:
        axis.plot(trade_numbers, equity_curves[simulation_index], linewidth=0.8, alpha=0.2)

    axis.plot(trade_numbers, original_equity_curve, linewidth=2.5, label="Original equity")

    axis.axhline(y=0, linewidth=1, linestyle="--")

    axis.set_title("Monte Carlo simulated equity curves")
    axis.set_xlabel("Trade number")
    axis.set_ylabel("Cumulative net result")
    axis.grid(alpha=0.3)
    axis.legend()

    figure.tight_layout()
    figure.savefig(output_path, dpi=300)
    plt.close(figure)