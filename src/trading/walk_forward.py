from src.features.impulse_strategy_features import add_impulse_strategy_features
from src.strategies.impulse_strategy import generate_signals
from src.ga.individual import create_initial_population
from src.ga.evolution import make_new_population
from src.trading.backtester import backtester
from src.ga.individual import copy_individual
from src.fitness.metrics import net_profit

class WalkForwardWindow:

    def __init__(self, train_start, train_end, test_start, test_end):
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start
        self.test_end = test_end

class WalkForwardResult:

    def __init__(self, window, best_individual, train_fitness, test_fitness):
        self.window = window
        self.best_individual = best_individual
        self.train_fitness = train_fitness
        self.test_fitness = test_fitness

def create_walk_forward_windows(df_length, train_size, test_size, step_size):

    windows = []

    number_of_windows = ((df_length - train_size - test_size) // step_size) + 1
    
    for i in range(number_of_windows):

        train_start =  i * step_size
        train_end  = train_size + i * step_size 
        test_start = train_size + i * step_size 
        test_end = train_size + test_size + i * step_size

        windows.append(WalkForwardWindow(train_start, train_end, test_start, test_end))

    return windows 

def run_walk_forward(df, windows, number_of_generations, population_size, fitness_function, tick_value, commission, maximum_holding_bars, patience):

    results = []

    for window in windows:

        train_df = df.iloc[window.train_start:window.train_end].copy()
        test_df = df.iloc[window.test_start:window.test_end].copy()

        train_df = add_impulse_strategy_features(train_df)
        test_df = add_impulse_strategy_features(test_df)

        population = create_initial_population(train_df, population_size, fitness_function, tick_value, commission, maximum_holding_bars)

        current_best_individual = max(population, key=lambda individual: individual.fitness)

        train_signal_df = generate_signals(train_df.copy(), current_best_individual)

        original_trades = backtester(train_signal_df, current_best_individual, maximum_holding_bars)

        print(f"Generation #0")
        current_best_individual.print_parameters()
        print(f"Number of trades: {len(original_trades)}")
        print(f"Profit: {net_profit(original_trades, tick_value, commission)}")
        print("")

        generations_without_improvement = 0
        best_fitness = current_best_individual.fitness
        last_best_individual = current_best_individual

        for i in range(number_of_generations):

            population = make_new_population(train_df, population, fitness_function, tick_value, commission, maximum_holding_bars)

            current_best_individual = max(population, key=lambda individual: individual.fitness)

            train_signal_df = generate_signals(train_df.copy(), current_best_individual)

            train_trades = backtester(train_signal_df, current_best_individual, maximum_holding_bars)

            if current_best_individual.fitness > best_fitness:
                best_fitness = current_best_individual.fitness
                generations_without_improvement = 0
                last_best_individual = current_best_individual
            else:
                generations_without_improvement += 1

            if generations_without_improvement >= patience:

                print(f"Early stopping at generation #{i+1}")
                last_best_individual.print_parameters()
                print(f"Number of trades: {len(train_trades)}")
                print(f"Profit: {net_profit(train_trades, tick_value, commission)}")
                print("")
                
                break

            print(f"Generation #{i+1}")
            current_best_individual.print_parameters()
            print(f"Number of trades: {len(train_trades)}")
            print(f"Profit: {net_profit(train_trades, tick_value, commission)}")
            print("")
        
        best_individual_copy_for_test = copy_individual(last_best_individual)

        test_df = generate_signals(test_df,best_individual_copy_for_test)

        test_trades = backtester(test_df, best_individual_copy_for_test, maximum_holding_bars)

        test_fitness = fitness_function(test_trades, tick_value, commission)

        best_individual_copy_for_test.fitness = test_fitness

        results.append(WalkForwardResult(window, last_best_individual, last_best_individual.fitness, best_individual_copy_for_test.fitness))

        print(f"Best trained individual on test data:")
        best_individual_copy_for_test.print_parameters()
        print(f"Number of trades: {len(test_trades)}")
        print(f"Profit: {net_profit(test_trades, tick_value, commission)}")
        print("")
    
    return results