from pathlib import Path
from datetime import time, datetime

from multiprocessing import cpu_count

from data.helpers.data_loader import load_data
from data.helpers.filter_data import filter_trading_hours
from data.helpers.create_csv import create_csv

from src.strategies.impulse_strategy.impulse_strategy_features import add_impulse_strategy_features
from src.strategies.impulse_strategy.impulse_strategy_signals import generate_impulse_signals

from src.trading.walk_forward import create_rolling_walk_forward_windows_by_days
from src.trading.walk_forward import create_expanding_walk_forward_windows_by_days
from src.trading.walk_forward import run_walk_forward

from src.fitness.fitness_functions import drawdown_adjusted_fitness

def main():
    
    print("Start of the program at:")
    start_time = datetime.now()
    print(start_time)
    print("")

    NUMBER_OF_GENERATIONS = 10
    POPULATION_SIZE = 10

    MAXIMUM_HOLDING_BARS = 100
    PATIENCE = 25
    NUMBER_OF_ITERATIONS = 2

    TICK_VALUE = 5
    COMMISSION = 4

    USE_PARALLEL = False
    N_JOBS = cpu_count() - 2  # number of CPU cores to use

    FITNESS_FUNCTIONS = [drawdown_adjusted_fitness]

    print("Loading Data...")
    start_loading = datetime.now()
    print("")

    df = load_data("data/market_data/NQ-1Y.txt")

    print("Data Loaded!")
    end_loading = datetime.now()
    print(f"total_loading_time: {end_loading - start_loading}")
    print("")

    print("Filtering Data...")
    start_filtering = datetime.now()
    print("")

    sessions = [
        (time(14, 30), time(17, 30)),
        (time(20, 0), time(23, 0))
    ]

    df = filter_trading_hours(df, sessions)

    print("Data Filtered!")
    end_filtering = datetime.now()
    print(f"total_loading_time: {end_filtering - start_filtering}")
    print("")

    print("Precomputing...")
    start_precomputation = datetime.now()
    print(start_precomputation)
    print("")

    df = add_impulse_strategy_features(df)

    print("End of precomputation")
    end_precomputation = datetime.now()
    print(end_precomputation)
    print(f"precomputation time: {end_precomputation - start_precomputation}")
    print("")

    TEST_DAYS = 1
    STEP_DAYS = 1
    INITIAL_TRAIN_DAYS = 2

    results_folder = Path("results_1")
    expanding_folder = results_folder / "expanding"
    rolling_folder = results_folder / "rolling"

    # Expanding walk-forward
    for fitness_function in FITNESS_FUNCTIONS:

        fitness_function_path = expanding_folder / fitness_function.__name__

        windows = create_expanding_walk_forward_windows_by_days(
            df,
            INITIAL_TRAIN_DAYS,
            TEST_DAYS,
            STEP_DAYS
        )

        for i in range(1, NUMBER_OF_ITERATIONS + 1):

            repetition_folder = fitness_function_path / f"rep_{i}"
            repetition_folder.mkdir(parents=True, exist_ok=True)

            if len(windows) == 0:
                continue

            (
                walk_forward_results,
                walk_forward_trades,
                generation_results,
                generation_best_individuals
            ) = run_walk_forward(
                df,
                windows,
                NUMBER_OF_GENERATIONS,
                POPULATION_SIZE,
                generate_impulse_signals,
                fitness_function,
                TICK_VALUE,
                COMMISSION,
                MAXIMUM_HOLDING_BARS,
                PATIENCE,
                USE_PARALLEL,
                N_JOBS
            )

            create_csv(
                walk_forward_results,
                walk_forward_trades,
                generation_results,
                generation_best_individuals,
                repetition_folder
            )

    # Rolling walk-forward
    TRAIN_SIZES = {
        "2_weeks": 1,
        "1_month": 2,
        "2_months": 3,
    }

    for fitness_function in FITNESS_FUNCTIONS:

        fitness_function_path = rolling_folder / fitness_function.__name__

        for train_days_name, train_days_size in TRAIN_SIZES.items():

            train_size_path = fitness_function_path / train_days_name

            windows = create_rolling_walk_forward_windows_by_days(
                df,
                train_days_size,
                TEST_DAYS,
                STEP_DAYS
            )

            for i in range(1, NUMBER_OF_ITERATIONS + 1):

                repetition_folder = train_size_path / f"rep_{i}"
                repetition_folder.mkdir(parents=True, exist_ok=True)

                if len(windows) == 0:
                    continue

                (
                    walk_forward_results,
                    walk_forward_trades,
                    generation_results,
                    generation_best_individuals
                ) = run_walk_forward(
                    df,
                    windows,
                    NUMBER_OF_GENERATIONS,
                    POPULATION_SIZE,
                    generate_impulse_signals,
                    fitness_function,
                    TICK_VALUE,
                    COMMISSION,
                    MAXIMUM_HOLDING_BARS,
                    PATIENCE,
                    USE_PARALLEL,
                    N_JOBS
                )

                create_csv(
                    walk_forward_results,
                    walk_forward_trades,
                    generation_results,
                    generation_best_individuals,
                    repetition_folder
                )

    print("End of the program at:")
    end_time = datetime.now()
    print(end_time)
    print(f"total time: {end_time - start_time}")


if __name__ == "__main__":
    main()