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

from analysis.create_csv import create_csv

from datetime import datetime

print("Start of the program at:")
start_time = datetime.now()
print(start_time)

NUMBER_OF_GENERATIONS = 10
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

## daily_counts = df.groupby("Date").size()
## ONE_WEEK = int(daily_counts.rolling(5).sum().median()) 
## TWO_WEEKS = int(daily_counts.rolling(10).sum().median()) 
## ONE_MONTH = int(daily_counts.rolling(20).sum().median()) 
##TWO_MONTHS = int(daily_counts.rolling(40).sum().median())

TEST_SIZE = ONE_DAY
STEP_SIZE = ONE_DAY

INITIAL_TRAIN_SIZE = ONE_DAY

results_folder = Path("results_1")
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
        
        if len(windows) == 0:
            continue

        walk_forward_results, generation_train_results, generation_test_results, walk_forward_trades, generation_test_trades  = run_walk_forward(df, 
                                                                                                            windows, 
                                                                                                            NUMBER_OF_GENERATIONS, 
                                                                                                            POPULATION_SIZE, 
                                                                                                            fitness_function, 
                                                                                                            TICK_VALUE, 
                                                                                                            COMMISSION, 
                                                                                                            MAXIMUM_HOLDING_BARS, 
                                                                                                            PATIENCE)
        

        create_csv(walk_forward_results, generation_train_results, generation_test_results, walk_forward_trades, generation_test_trades, repetition_folder)

## rolling
TRAIN_SIZES = {
    "1_day": ONE_DAY,
    "2_days": TWO_DAYS,
    "3_days": THREE_DAYS,
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

            if len(windows) == 0:
                continue

            walk_forward_results, generation_train_results, generation_test_results, walk_forward_trades, generation_test_trades  = run_walk_forward(df, 
                                                                                                            windows, 
                                                                                                            NUMBER_OF_GENERATIONS, 
                                                                                                            POPULATION_SIZE, 
                                                                                                            fitness_function, 
                                                                                                            TICK_VALUE, 
                                                                                                            COMMISSION, 
                                                                                                            MAXIMUM_HOLDING_BARS, 
                                                                                                            PATIENCE)
            
            create_csv(walk_forward_results, generation_train_results, generation_test_results, walk_forward_trades, generation_test_trades, repetition_folder)

print("End of the program at:")
end_time = datetime.now()
print(end_time)
print(f"total time: {end_time - start_time}")