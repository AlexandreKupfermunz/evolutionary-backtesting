from pathlib import Path
import pandas as pd

from data.data_loader import load_data

from src.trading.walk_forward import create_rolling_walk_forward_windows
from src.trading.walk_forward import create_expanding_walk_forward_windows
from src.trading.walk_forward import run_walk_forward

from src.fitness.fitness_functions import net_profit_fitness
from src.fitness.fitness_functions import expectancy_fitness
from src.fitness.fitness_functions import drawdown_adjusted_fitness
from src.fitness.fitness_functions import balanced_fitness
from src.fitness.fitness_functions import robust_fitness

print("test")

NUMBERS_OF_GENERATIONS = 10
POPULATION_SIZE = 10

MAXIMUM_HOLDING_BARS = 200
PATIENCE = 10

TICK_VALUE = 5
COMMISSION = 4

FITNESS_FUNCTIONS = [balanced_fitness]

df = load_data("data/NQ-Sample_Data.txt")

DATA_SIZE = len(df)

CANDLES = 1000

ONE_DAY = CANDLES
TWO_DAYS = ONE_DAY * 2
THREE_DAYS = ONE_DAY * 3

TEST_SIZE = ONE_DAY
STEP_SIZE = ONE_DAY

INITIAL_TRAIN_SIZE = ONE_DAY

results_folder = Path("results")
expanding_folder = results_folder / "expanding"
rolling_folder = results_folder / "rolling"

## expanding 
for fitness_function in FITNESS_FUNCTIONS:

    fitness_function_path = expanding_folder / fitness_function.__name__

    ## numbers of iterations

    for i in range(1, 2):

        repetition_folder = fitness_function_path / f"rep_{i}"

        repetition_folder.mkdir(parents=True, exist_ok=True)

        windows = create_expanding_walk_forward_windows(DATA_SIZE, INITIAL_TRAIN_SIZE, TEST_SIZE, STEP_SIZE)
        walk_forward_results, generation_results = run_walk_forward(df, 
                                                                    windows, 
                                                                    NUMBERS_OF_GENERATIONS, 
                                                                    POPULATION_SIZE, 
                                                                    fitness_function, 
                                                                    TICK_VALUE, 
                                                                    COMMISSION, 
                                                                    MAXIMUM_HOLDING_BARS, 
                                                                    PATIENCE)
        
        walk_forward_df = pd.DataFrame([vars(result) for result in walk_forward_results])
        generation_df = pd.DataFrame([vars(result) for result in generation_results])

        walk_forward_csv = repetition_folder / "walk_forward_results.csv"
        generation_csv = repetition_folder / "generation_results.csv"

        walk_forward_df.to_csv(walk_forward_csv, index=False)
        generation_df.to_csv(generation_csv, index=False)

## rolling
TRAIN_SIZES = {
    "ONE_DAY": ONE_DAY,
    "TWO_DAYS": TWO_DAYS,
    "THREE_DAYS": THREE_DAYS,
}
for fitness_function in FITNESS_FUNCTIONS:

    fitness_function_path = rolling_folder / fitness_function.__name__

    ##different train sizes
    for train_size_name, train_size in TRAIN_SIZES.items():

        train_size_path = fitness_function_path / train_size_name

        ## numbers of iterations
        for i in range(1, 2):

            repetition_folder = train_size_path / f"rep_{i}"

            repetition_folder.mkdir(parents=True, exist_ok=True)

            windows = create_rolling_walk_forward_windows(DATA_SIZE, train_size, TEST_SIZE, STEP_SIZE)
            walk_forward_results, generation_results = run_walk_forward(df, 
                                                                        windows, 
                                                                        NUMBERS_OF_GENERATIONS, 
                                                                        POPULATION_SIZE, 
                                                                        fitness_function, 
                                                                        TICK_VALUE, 
                                                                        COMMISSION, 
                                                                        MAXIMUM_HOLDING_BARS, 
                                                                        PATIENCE)
            
            walk_forward_df = pd.DataFrame([vars(result) for result in walk_forward_results])
            generation_df = pd.DataFrame([vars(result) for result in generation_results])

            walk_forward_csv = repetition_folder / "walk_forward_results.csv"
            generation_csv = repetition_folder / "generation_results.csv"

            walk_forward_df.to_csv(walk_forward_csv, index=False)
            generation_df.to_csv(generation_csv, index=False)