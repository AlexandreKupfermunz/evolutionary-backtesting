from data.data_loader import load_data

from src.trading.walk_forward import create_rolling_walk_forward_windows
from src.trading.walk_forward import create_expanding_walk_forward_windows
from src.trading.walk_forward import run_walk_forward

from src.fitness.fitness_functions import net_profit_fitness
from src.fitness.fitness_functions import expectancy_fitness
from src.fitness.fitness_functions import drawdown_adjusted_fitness
from src.fitness.fitness_functions import balanced_fitness
from src.fitness.fitness_functions import robust_fitness

NUMBERS_OF_GENERATIONS = 200
POPULATION_SIZE = 100

MAXIMUM_HOLDING_BARS = 200
PATIENCE = 10

TICK_VALUE = 5
COMMISSION = 4

FITNESS_FUNCTIONS = [net_profit_fitness, expectancy_fitness, drawdown_adjusted_fitness, balanced_fitness, robust_fitness]

df = load_data("data/NQ-5D.txt")

DATA_SIZE = round(len(df) / 50_000) * 50_000

CANDLES_PER_DAY = int(df.groupby("Date").size().median())

ONE_WEEK = CANDLES_PER_DAY * 5

TEST_SIZE = ONE_WEEK
STEP_SIZE = ONE_WEEK

TWO_WEEKS = ONE_WEEK * 2
ONE_MONTH = ONE_WEEK * 4
TWO_MONTHS = ONE_WEEK * 8

INITIAL_TRAIN_SIZE = ONE_MONTH

## expanding 
for fitness_function in FITNESS_FUNCTIONS:
    ## numbers of iterations
    for _ in range(5):
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

## rolling
TRAIN_SIZES = [ONE_WEEK, TWO_WEEKS, ONE_MONTH, TWO_MONTHS]

for fitness_function in FITNESS_FUNCTIONS:

    ##different train sizes
    for train_size in TRAIN_SIZES:

        ## numbers of iterations
        for _ in range(5):
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