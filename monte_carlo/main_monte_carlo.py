from pathlib import Path

import pandas as pd

from monte_carlo.monte_carlo_metrics import calculate_trade_metrics
from monte_carlo.monte_carlo_metrics import equity_curve

from monte_carlo.monte_carlo_plots import plot_equity_curves
from monte_carlo.monte_carlo_plots import plot_longest_losing_streak_distribution
from monte_carlo.monte_carlo_plots import plot_max_drawdown_distribution
from monte_carlo.monte_carlo_plots import plot_net_profit_distribution
from monte_carlo.monte_carlo_plots import plot_profit_factor_distribution
from monte_carlo.monte_carlo_plots import plot_recovery_factor_distribution
from monte_carlo.monte_carlo_plots import plot_win_rate_distribution

from monte_carlo.monte_carlo_simulation import monte_carlo_simulation

experiment_folder = Path("experiments/default_experiment")

rep_folder = Path("experiments/default_experiment/results/rolling/drawdown_adjusted_fitness/1_days/rep_1" )

trades_file_path = (rep_folder / "walk_forward_trades.csv")

output_folder = (experiment_folder / "monte_carlo_analysis")

number_of_simulations = 5000
random_seed = 42
number_of_equity_curves_to_plot = 100

if not trades_file_path.exists():
    raise FileNotFoundError(f"Trades file not found: {trades_file_path}")

output_folder.mkdir(parents=True,exist_ok=True,)

print("Loading walk-forward trades...")

trades_df = pd.read_csv(trades_file_path)

if "result" not in trades_df.columns:
    raise ValueError("The trades CSV must contain a 'result' column.")

trade_results = trades_df["result"].to_numpy(dtype=float)

if len(trade_results) == 0:
    raise ValueError("The trades CSV does not contain any trades.")

print(f"Number of trades: {len(trade_results)}")

print(f"Running {number_of_simulations} ""Monte Carlo simulations...")

simulation_metrics, simulated_equity_curves = (
    monte_carlo_simulation(trade_results=trade_results, number_of_simulations=number_of_simulations, random_seed=random_seed))

original_metrics = calculate_trade_metrics(trade_results)

original_equity_curve = equity_curve(trade_results)

print("Creating equity curves plot...")

plot_equity_curves(
    equity_curves=simulated_equity_curves,
    original_equity_curve=original_equity_curve,
    output_path=output_folder / "equity_curves.png",
    number_of_curves_to_plot=number_of_equity_curves_to_plot,
    random_seed=random_seed,
)

print("Creating net profit distribution...")

plot_net_profit_distribution(
    simulation_metrics=simulation_metrics,
    output_path=output_folder / "net_profit_distribution.png",
    original_net_profit=original_metrics.net_profit)

print("Creating maximum drawdown distribution...")

plot_max_drawdown_distribution(
    simulation_metrics=simulation_metrics,
    output_path=output_folder / "max_drawdown_distribution.png",
    original_max_drawdown=original_metrics.max_drawdown)

print("Creating losing streak distribution...")

plot_longest_losing_streak_distribution(
    simulation_metrics=simulation_metrics,
    output_path=output_folder / "longest_losing_streak_distribution.png",
    original_losing_streak=original_metrics.longest_losing_streak)

print("Creating profit factor distribution...")

plot_profit_factor_distribution(
    simulation_metrics=simulation_metrics,
    output_path=output_folder / "profit_factor_distribution.png",
    original_profit_factor=original_metrics.profit_factor)

print("Creating recovery factor distribution...")

plot_recovery_factor_distribution(
    simulation_metrics=simulation_metrics,
    output_path=output_folder / "recovery_factor_distribution.png",
    original_recovery_factor=original_metrics.recovery_factor)

print("Creating win rate distribution...")

plot_win_rate_distribution(
    simulation_metrics=simulation_metrics,
    output_path=output_folder / "win_rate_distribution.png",
    original_win_rate=original_metrics.win_rate)

print()
print("Monte Carlo analysis completed.")
print(f"Plots saved in: {output_folder}")
