from src.ga.individual import create_initial_population
from src.ga.evolution import make_new_population
from src.trading.backtester import backtester
from src.ga.individual import copy_individual

from src.fitness.fitness_functions import net_profit_fitness
from src.fitness.fitness_functions import expectancy_fitness
from src.fitness.fitness_functions import drawdown_adjusted_fitness
from src.fitness.fitness_functions import losing_streak_fitness
from src.fitness.fitness_functions import robust_fitness

from src.ga.population_statistics import PopulationStatistics

from src.fitness.fitness_metrics import calculate_fitness_metrics

class WalkForwardWindow:

    def __init__(self, window_id, train_start, train_end, test_start, test_end):
        self.window_id = window_id
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start
        self.test_end = test_end

    def to_dict(self):

        return({
            "window_id": self.window_id,
            "train_start": self.train_start,
            "train_end": self.train_end,
            "test_start": self.test_start,
            "test_end": self.test_end
        })

class WalkForwardResult:

    def __init__(
        self,
        window,
        best_individual,
        raw_test_fitness,
        test_fitness,
        test_fitness_multiplier,
        test_metrics
    ):
        self.window = window
        self.best_individual = best_individual
        self.raw_test_fitness = raw_test_fitness
        self.test_fitness = test_fitness
        self.test_fitness_multiplier = test_fitness_multiplier
        self.test_metrics = test_metrics

    def to_dict(self):

        row = {}

        row.update(self.window.to_dict())

        row.update(self.best_individual.to_dict())

        row.update({
            "raw_test_fitness": self.raw_test_fitness,
            "test_fitness": self.test_fitness,
            "test_fitness_multiplier": self.test_fitness_multiplier
        })

        row.update(self.test_metrics.to_dict())

        return row

class GenerationResult:

    def __init__(
        self,
        window,
        generation,
        patience_counter,
        population_statistics
    ):
        self.window = window
        self.generation = generation
        self.patience_counter = patience_counter
        self.population_statistics = population_statistics
        

    def to_dict(self):

        row = {}

        row.update({"generation": self.generation})
        row.update(self.window.to_dict())
        row.update(self.population_statistics.to_dict())
        row.update({"patience_counter": self.patience_counter})

        return row
    
class BestIndividualResults:

    def __init__(
            self,
            dataset_type,
            window,
            generation,
            best_individual,
            fitness_metrics,
    ):
        self.dataset_type=dataset_type
        self.window=window
        self.generation=generation
        self.best_individual = best_individual
        self.fitness_metrics = fitness_metrics

    def to_dict(self):

        row = {}

        row.update({"dataset_type": self.dataset_type})
        row.update(self.window.to_dict())
        row.update({"generation": self.generation})
        row.update(self.best_individual.to_dict())
        row.update(self.fitness_metrics.to_dict())

        return row

def create_rolling_walk_forward_windows(df_length, train_size, test_size, step_size):

    windows = []

    number_of_windows = ((df_length - train_size - test_size) // step_size) + 1

    window_id = 1
    
    for i in range(number_of_windows):

        offset = i * step_size

        train_start = offset
        train_end = train_size + offset
        test_start = train_end
        test_end = test_start + test_size

        windows.append(WalkForwardWindow(window_id, train_start, train_end, test_start, test_end))

        window_id += 1

    return windows 

def create_expanding_walk_forward_windows(df_length, train_size, test_size, step_size):

    windows = []

    number_of_windows = ((df_length - train_size - test_size) // step_size) + 1

    window_id = 0
    
    for i in range(number_of_windows):

        offset = i * step_size

        train_start = 0
        train_end = train_size + offset
        test_start = train_end
        test_end = test_start + test_size

        windows.append(WalkForwardWindow(window_id, train_start, train_end, test_start, test_end))

        window_id += 1

    return windows 

def create_day_index_map(df, date_column="Date"):

    df = df.reset_index(drop=True).copy()

    day_index_map = {}

    for date, group in df.groupby(date_column, sort=True):
        
        start_index = group.index[0]
        end_index = group.index[-1] + 1

        day_index_map[date] = {
            "start": start_index,
            "end": end_index
        }

    unique_dates = list(day_index_map.keys())

    return unique_dates, day_index_map

def create_rolling_walk_forward_windows_by_days(df, train_days, test_days, step_days, date_column="Date"):
    
    windows = []

    unique_dates, day_index_map = create_day_index_map(df, date_column)

    window_id = 1
    start_day_index = 0

    while True:

        train_start_day_index = start_day_index
        train_end_day_index = train_start_day_index + train_days

        test_start_day_index = train_end_day_index
        test_end_day_index = test_start_day_index + test_days

        if test_end_day_index > len(unique_dates):
            break

        train_start_date = unique_dates[train_start_day_index]
        train_end_date = unique_dates[train_end_day_index - 1]

        test_start_date = unique_dates[test_start_day_index]
        test_end_date = unique_dates[test_end_day_index - 1]

        train_start = day_index_map[train_start_date]["start"]
        train_end = day_index_map[train_end_date]["end"]

        test_start = day_index_map[test_start_date]["start"]
        test_end = day_index_map[test_end_date]["end"]

        windows.append(WalkForwardWindow(window_id, train_start, train_end, test_start, test_end))

        window_id += 1
        start_day_index += step_days

    return windows

def create_expanding_walk_forward_windows_by_days(df, initial_train_days, test_days, step_days, date_column="Date"):

    windows = []

    unique_dates, day_index_map = create_day_index_map(df, date_column)

    window_id = 1
    train_start_day_index = 0
    train_end_day_index = initial_train_days

    while True:

        test_start_day_index = train_end_day_index
        test_end_day_index = test_start_day_index + test_days

        if test_end_day_index > len(unique_dates):
            break

        train_start_date = unique_dates[train_start_day_index]
        train_end_date = unique_dates[train_end_day_index - 1]

        test_start_date = unique_dates[test_start_day_index]
        test_end_date = unique_dates[test_end_day_index - 1]

        train_start = day_index_map[train_start_date]["start"]
        train_end = day_index_map[train_end_date]["end"]

        test_start = day_index_map[test_start_date]["start"]
        test_end = day_index_map[test_end_date]["end"]

        windows.append(WalkForwardWindow(window_id, train_start, train_end, test_start, test_end))

        window_id += 1
        train_end_day_index += step_days

    return windows

def calculate_test_fitness_multiplier( train_df, test_df, date_column="Date"):

    train_days = train_df[date_column].nunique()
    test_days = test_df[date_column].nunique()

    if train_days == 0:
        raise ValueError("The training dataset contains no trading days.")

    if test_days == 0:
        raise ValueError("The testing dataset contains no trading days.")

    multiplier = train_days / test_days

    return multiplier

def adjust_test_fitness(
    raw_test_fitness,
    multiplier,
    fitness_function,
    performance_metrics
):
    
    if performance_metrics.number_of_trades == 0:
        return raw_test_fitness

    if fitness_function is expectancy_fitness:
        return raw_test_fitness

    if fitness_function is losing_streak_fitness:
        return raw_test_fitness * multiplier ** 1.5

    if fitness_function in {
        net_profit_fitness,
        drawdown_adjusted_fitness,
        robust_fitness,
    }:
        return raw_test_fitness * multiplier

    raise ValueError(
        f"No test-fitness adjustment defined for "
        f"{fitness_function.__name__}"
    )

def run_walk_forward(df, 
                     windows, 
                     number_of_generations, 
                     population_size, 
                     generate_strategy_signals, 
                     fitness_function, 
                     tick_value, 
                     commission, 
                     maximum_holding_bars, 
                     patience,
                     repetition_id,
                     use_parallel=False,
                     n_jobs=None,
                     progress_callback=None):

    walk_forward_results = []
    walk_forward_trades = [] 

    generation_results = []
    generation_best_individuals = []

    for window in windows:

        train_df = df.iloc[window.train_start:window.train_end]
        test_df = df.iloc[window.test_start:window.test_end]

        test_fitness_multiplier = calculate_test_fitness_multiplier( train_df=train_df, test_df=test_df, date_column="Date")

        population = create_initial_population(train_df, population_size, generate_strategy_signals, fitness_function, tick_value, commission, maximum_holding_bars, use_parallel, n_jobs)
        population_statistics = PopulationStatistics(population)

        current_best_individual = max(population, key=lambda individual: individual.fitness)

        train_signal_df = generate_strategy_signals(train_df, current_best_individual)
        original_train_trades = backtester(train_signal_df, current_best_individual, maximum_holding_bars)
        
        generation_results.append(create_generation_result(window, 0, 0, population_statistics))
        generation_best_individuals.append(create_best_individual_result("train", window, 0, current_best_individual, original_train_trades, fitness_function, tick_value, commission))

        test_signal_df = generate_strategy_signals(test_df, current_best_individual)
        original_test_trades = backtester(test_signal_df, current_best_individual, maximum_holding_bars)

        generation_best_individuals.append(create_best_individual_result("test", window, 0, current_best_individual, original_test_trades, fitness_function, tick_value, commission, test_fitness_multiplier))

        original_train_metrics = calculate_fitness_metrics(original_train_trades, tick_value, commission)
        original_test_metrics = calculate_fitness_metrics(original_test_trades, tick_value, commission)
        original_raw_test_fitness = fitness_function(original_test_metrics)
        original_test_fitness = adjust_test_fitness(original_raw_test_fitness, test_fitness_multiplier, fitness_function, original_test_metrics)
        
        generation_print(0, current_best_individual, original_train_metrics, original_test_metrics, original_test_fitness)

        generations_without_improvement = 0
        best_generation_so_far = 0
        best_fitness = current_best_individual.fitness
        best_individual_so_far = copy_individual(current_best_individual)

        for i in range(1, number_of_generations+1):

            population = make_new_population(train_df, population, generate_strategy_signals, fitness_function, tick_value, commission, maximum_holding_bars, use_parallel, n_jobs)
            population_statistics = PopulationStatistics(population)

            current_best_individual = max(population, key=lambda individual: individual.fitness)

            if current_best_individual.fitness > best_fitness:
                best_fitness = current_best_individual.fitness
                best_individual_so_far = copy_individual(current_best_individual)
                generations_without_improvement = 0
                best_generation_so_far = i
            else:
                generations_without_improvement += 1

            current_train_signal_df = generate_strategy_signals(train_df, current_best_individual)
            current_train_trades = backtester(current_train_signal_df, current_best_individual, maximum_holding_bars)

            generation_results.append(create_generation_result(window, i, generations_without_improvement, population_statistics))
            generation_best_individuals.append(create_best_individual_result("train", window, i, current_best_individual, current_train_trades, fitness_function, tick_value, commission))

            current_test_signal_df = generate_strategy_signals(test_df, current_best_individual)
            current_test_trades = backtester(current_test_signal_df, current_best_individual, maximum_holding_bars)

            generation_best_individuals.append(create_best_individual_result("test", window, i, current_best_individual, current_test_trades, fitness_function, tick_value, commission, test_fitness_multiplier))

            current_train_metrics = calculate_fitness_metrics(current_train_trades, tick_value, commission)
            current_test_metrics = calculate_fitness_metrics(current_test_trades, tick_value, commission)
            raw_test_fitness = fitness_function(current_test_metrics)
            test_fitness = adjust_test_fitness(raw_test_fitness, test_fitness_multiplier, fitness_function, current_test_metrics)

            if generations_without_improvement >= patience:

                print("Early stopping")
                generation_print(i, current_best_individual, current_train_metrics, current_test_metrics, test_fitness)
                
                break

            if (i)%5==0:
                generation_print(i, current_best_individual, current_train_metrics, current_test_metrics, test_fitness)
        
        best_individual_copy_for_test = copy_individual(best_individual_so_far)

        test_signal_df = generate_strategy_signals(test_df, best_individual_copy_for_test)

        test_trades = backtester(test_signal_df, best_individual_copy_for_test, maximum_holding_bars)

        test_metrics = calculate_fitness_metrics(test_trades, tick_value, commission)

        raw_test_fitness = fitness_function(test_metrics)

        test_fitness = adjust_test_fitness(raw_test_fitness, test_fitness_multiplier, fitness_function, test_metrics)

        best_individual_copy_for_test.fitness = test_fitness 

        walk_forward_results.append(WalkForwardResult(window = window, 
                                        best_individual = best_individual_copy_for_test, 
                                        raw_test_fitness = raw_test_fitness,
                                        test_fitness = test_fitness,
                                        test_fitness_multiplier = test_fitness_multiplier,
                                        test_metrics = test_metrics))
        
        for trade in test_trades:
            trade.window = window
            trade.generation = best_generation_so_far
            trade.repetition_id = repetition_id
            walk_forward_trades.append(trade)

        if progress_callback is not None:
            progress_callback()

        print(f"Best trained individual on test data:")
        best_individual_copy_for_test.print_parameters()
        print(f"Number of trades: {len(test_trades)}")
        print(f"Profit: {test_metrics.net_profit}")
        print("")
    
    return walk_forward_results, walk_forward_trades, generation_results, generation_best_individuals

def generation_print(generation, individual, train_metrics, test_metrics, test_fitness):

    print(f"Generation #{generation}")
    individual.print_parameters()
    print(f"Number of trades: {train_metrics.number_of_trades}")
    print(f"Profit: {train_metrics.net_profit}")
    print("")

    print(f"Current test results")
    print(f"Number of trades: {test_metrics.number_of_trades}")
    print(f"Test fitness: {test_fitness}")
    print(f"Profit: {test_metrics.net_profit}")
    print("")

def create_generation_result(window, generation, patience_counter, population_statistics):

    return GenerationResult(
        window=window,
        generation=generation,
        patience_counter=patience_counter,
        population_statistics=population_statistics,
    )

def create_best_individual_result(dataset_type, window, generation, individual, trades, fitness_function, tick_value, commission, fitness_multiplier=1.0):

    individual_copy = copy_individual(individual)

    fitness_metrics = calculate_fitness_metrics(trades, tick_value, commission)

    raw_fitness = fitness_function(fitness_metrics)

    if dataset_type == "test":
        result_fitness = adjust_test_fitness(raw_fitness, fitness_multiplier, fitness_function, fitness_metrics)
    else:
        result_fitness = raw_fitness

    individual_copy.fitness = result_fitness

    return BestIndividualResults(
        dataset_type=dataset_type,
        window=window,
        generation=generation,
        best_individual=individual_copy,
        fitness_metrics=fitness_metrics,
    )