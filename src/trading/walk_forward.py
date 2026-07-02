from src.features.impulse_strategy_features import add_impulse_strategy_features
from src.strategies.impulse_strategy import generate_impulse_signals
from src.ga.individual import create_initial_population
from src.ga.evolution import make_new_population
from src.trading.backtester import backtester
from src.ga.individual import copy_individual

from src.trading.performance import calculate_performance_metrics

from src.fitness.metrics import net_profit
from src.fitness.metrics import gross_profit
from src.fitness.metrics import gross_loss
from src.fitness.metrics import biggest_losing_streak
from src.fitness.metrics import profit_factor
from src.fitness.metrics import max_drawdown
from src.fitness.metrics import win_rate
from src.fitness.metrics import average_trade
from src.fitness.metrics import biggest_loss

from src.trading.trade import Trade

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

    def __init__(self, 
                window,
                best_individual,
                test_fitness,
                test_metrics):  
        self.window = window
        self.best_individual = best_individual
        self.test_fitness = test_fitness
        self.test_metrics = test_metrics

    def to_dict(self):

        row = {}

        row.update(self.window.to_dict())

        row.update(self.best_individual.to_dict())

        row.update({"test_fitness": self.test_fitness})

        row.update(self.test_metrics.to_dict())
        
        return row

class GenerationResult:

    def __init__(
        self,
        dataset_type,
        window,
        generation,
        best_individual,
        metrics,
        patience_counter,
    ):
        self.dataset_type = dataset_type
        self.window = window
        self.generation = generation
        self.best_individual = best_individual
        self.metrics = metrics
        self.patience_counter = patience_counter

    def to_dict(self):

        row = {}

        row.update({
            "dataset_type": self.dataset_type,
            "generation": self.generation,
        })

        row.update(self.window.to_dict())
        row.update(self.best_individual.to_dict())
        row.update(self.metrics.to_dict())
        row.update({"patience_counter": self.patience_counter})

        return row

def create_rolling_walk_forward_windows(df_length, train_size, test_size, step_size):

    windows = []

    number_of_windows = ((df_length - train_size - test_size) // step_size) + 1

    window_id = 0
    
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

def run_walk_forward(df, windows, number_of_generations, population_size, fitness_function, tick_value, commission, maximum_holding_bars, patience):

    walk_forward_results = []
    walk_forward_trades = [] 

    generation_train_results = []
    generation_test_results = []
    generation_test_trades = []

    for window in windows:

        train_df = df.iloc[window.train_start:window.train_end].copy()
        test_df = df.iloc[window.test_start:window.test_end].copy()

        train_df = add_impulse_strategy_features(train_df)
        test_df = add_impulse_strategy_features(test_df)

        population = create_initial_population(train_df, population_size, fitness_function, tick_value, commission, maximum_holding_bars)

        current_best_individual = max(population, key=lambda individual: individual.fitness)

        train_signal_df = generate_impulse_signals(train_df, current_best_individual)
        original_train_trades = backtester(train_signal_df, current_best_individual, maximum_holding_bars)
        
        generation_train_results.append(create_generation_result("train", window, 0, current_best_individual, original_train_trades, fitness_function, tick_value, commission, 0))

        test_signal_df = generate_impulse_signals(test_df, current_best_individual)
        original_test_trades = backtester(test_signal_df, current_best_individual, maximum_holding_bars)

        for trade in original_test_trades:
            trade.window = window
            trade.generation = 0
            generation_test_trades.append(trade)

        generation_test_results.append(create_generation_result("test", window, 0, current_best_individual, original_test_trades, fitness_function, tick_value, commission, 0))
        
        original_test_fitness = fitness_function(original_test_trades, tick_value, commission)

        generation_print(0, current_best_individual, original_train_trades, original_test_trades, original_test_fitness, tick_value, commission)

        generations_without_improvement = 0
        best_generation_so_far = 0
        best_fitness = current_best_individual.fitness
        best_individual_so_far = copy_individual(current_best_individual)

        for i in range(1, number_of_generations):

            population = make_new_population(train_df, population, fitness_function, tick_value, commission, maximum_holding_bars)

            current_best_individual = max(population, key=lambda individual: individual.fitness)

            if current_best_individual.fitness > best_fitness:
                best_fitness = current_best_individual.fitness
                generations_without_improvement = 0
                best_individual_so_far = copy_individual(current_best_individual)
                best_generation_so_far = i
            else:
                generations_without_improvement += 1

            current_train_signal_df = generate_impulse_signals(train_df, current_best_individual)
            current_train_trades = backtester(current_train_signal_df, current_best_individual, maximum_holding_bars)

            generation_train_results.append(create_generation_result("train", window, i, current_best_individual, current_train_trades, fitness_function, tick_value, commission, generations_without_improvement))

            current_test_signal_df = generate_impulse_signals(test_df, current_best_individual)
            current_test_trades = backtester(current_test_signal_df, current_best_individual, maximum_holding_bars)

            generation_test_results.append(create_generation_result("test", window, i, current_best_individual, current_test_trades, fitness_function, tick_value, commission, generations_without_improvement))

            for trade in current_test_trades:
                trade.window = window
                trade.generation = i
                generation_test_trades.append(trade)

            test_fitness = fitness_function(current_test_trades, tick_value, commission)

            if generations_without_improvement >= patience:

                print("Early stopping")
                generation_print(i, current_best_individual, current_train_trades, current_test_trades, test_fitness, tick_value, commission)
                
                break

            generation_print(i, current_best_individual, current_train_trades, current_test_trades, test_fitness, tick_value, commission)
        
        best_individual_copy_for_test = copy_individual(best_individual_so_far)

        test_signal_df = generate_impulse_signals(test_df, best_individual_copy_for_test)

        test_trades = backtester(test_signal_df, best_individual_copy_for_test, maximum_holding_bars)

        test_fitness = fitness_function(test_trades, tick_value, commission)

        best_individual_copy_for_test.fitness = test_fitness

        test_metrics = calculate_performance_metrics(test_trades, tick_value, commission)

        walk_forward_results.append(WalkForwardResult(window = window, 
                                         best_individual = best_individual_copy_for_test, 
                                         test_fitness = test_fitness,
                                         test_metrics = test_metrics))
        
        for trade in test_trades:
            trade.window = window
            trade.generation = best_generation_so_far
            walk_forward_trades.append(trade)
            

        print(f"Best trained individual on test data:")
        best_individual_copy_for_test.print_parameters()
        print(f"Number of trades: {len(test_trades)}")
        print(f"Profit: {net_profit(test_trades, tick_value, commission)}")
        print("")
    
    return walk_forward_results, generation_train_results, generation_test_results, walk_forward_trades, generation_test_trades

def generation_print(generation, individual, train_trades, test_trades, test_fitness, tick_value, commission):

    print(f"Generation #{generation}")
    individual.print_parameters()
    print(f"Number of trades: {len(train_trades)}")
    print(f"Profit: {net_profit(train_trades, tick_value, commission)}")
    print("")

    print(f"Current test results")
    print(f"Number of trades: {len(test_trades)}")
    print(f"Test fitness: {test_fitness}")
    print(f"Profit: {net_profit(test_trades, tick_value, commission)}")
    print("")

def create_generation_result(dataset_type, window, generation, individual, trades, fitness_function, tick_value, commission, patience_counter):
    
    individual_copy = copy_individual(individual)

    trades_fitness = fitness_function(trades, tick_value, commission)
    individual_copy.fitness = trades_fitness

    metrics = calculate_performance_metrics(trades, tick_value, commission)

    return GenerationResult(
        dataset_type=dataset_type,
        window=window,
        generation=generation,
        best_individual=individual_copy,
        metrics=metrics,
        patience_counter=patience_counter,
    )