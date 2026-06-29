from src.features.impulse_strategy_features import add_impulse_strategy_features
from src.strategies.impulse_strategy import generate_signals
from src.ga.individual import create_initial_population
from src.ga.evolution import make_new_population
from src.trading.backtester import backtester
from src.ga.individual import copy_individual

from src.fitness.metrics import net_profit
from src.fitness.metrics import gross_profit
from src.fitness.metrics import gross_loss
from src.fitness.metrics import biggest_losing_streak
from src.fitness.metrics import profit_factor
from src.fitness.metrics import max_drawdown
from src.fitness.metrics import win_rate
from src.fitness.metrics import average_trade
from src.fitness.metrics import biggest_loss

class WalkForwardWindow:

    def __init__(self, train_start, train_end, test_start, test_end):
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start
        self.test_end = test_end

class WalkForwardResult:

    def __init__(self, 
                window,
                best_individual,
                train_fitness,
                test_fitness):  
        self.window = window
        self.best_individual = best_individual
        self.train_fitness = train_fitness
        self.test_fitness = test_fitness


class GenerationResult:

    def __init__(
        self,
        window,
        generation,
        best_individual,
        fitness,
        number_of_trades,
        net_profit,
        gross_profit,
        gross_loss,
        profit_factor,
        max_drawdown,
        win_rate,
        average_trade,
        biggest_loss,
        biggest_losing_streak,
        patience_counter,
    ):
        self.window = window
        self.generation = generation
        self.best_individual = best_individual
        self.fitness = fitness
        self.number_of_trades = number_of_trades
        self.net_profit = net_profit
        self.gross_profit = gross_profit
        self.gross_loss = gross_loss
        self.profit_factor = profit_factor
        self.max_drawdown = max_drawdown
        self.win_rate = win_rate
        self.average_trade = average_trade
        self.biggest_loss = biggest_loss
        self.biggest_losing_streak = biggest_losing_streak
        self.patience_counter = patience_counter

def create_rolling_walk_forward_windows(df_length, train_size, test_size, step_size):

    windows = []

    number_of_windows = ((df_length - train_size - test_size) // step_size) + 1
    
    for i in range(number_of_windows):

        offset = i * step_size

        train_start = offset
        train_end = train_size + offset
        test_start = train_end
        test_end = test_start + test_size

        windows.append(WalkForwardWindow(train_start, train_end, test_start, test_end))

    return windows 

def create_expanding_walk_forward_windows(df_length, train_size, test_size, step_size):

    windows = []

    number_of_windows = ((df_length - train_size - test_size) // step_size) + 1
    
    for i in range(number_of_windows):

        offset = i * step_size

        train_start = 0
        train_end = train_size + offset
        test_start = train_end
        test_end = test_start + test_size

        windows.append(WalkForwardWindow(train_start, train_end, test_start, test_end))

    return windows 

def run_walk_forward(df, windows, number_of_generations, population_size, fitness_function, tick_value, commission, maximum_holding_bars, patience):

    walk_forward_results = []
    generation_results = []

    for window in windows:

        train_df = df.iloc[window.train_start:window.train_end].copy()
        test_df = df.iloc[window.test_start:window.test_end].copy()

        train_df = add_impulse_strategy_features(train_df)
        test_df = add_impulse_strategy_features(test_df)

        population = create_initial_population(train_df, population_size, fitness_function, tick_value, commission, maximum_holding_bars)

        current_best_individual = max(population, key=lambda individual: individual.fitness)

        train_signal_df = generate_signals(train_df.copy(), current_best_individual)

        original_trades = backtester(train_signal_df, current_best_individual, maximum_holding_bars)

        generation_results.append(GenerationResult(
                                        window=window,
                                        generation=0,
                                        best_individual=current_best_individual,
                                        fitness=current_best_individual.fitness,
                                        number_of_trades=len(original_trades),
                                        net_profit=net_profit(original_trades, tick_value, commission),
                                        gross_profit=gross_profit(original_trades, tick_value, commission),
                                        gross_loss=gross_loss(original_trades, tick_value, commission),
                                        profit_factor=profit_factor(original_trades, tick_value, commission),
                                        max_drawdown=max_drawdown(original_trades, tick_value, commission),
                                        win_rate=win_rate(original_trades, tick_value, commission),
                                        average_trade=average_trade(original_trades, tick_value, commission),
                                        biggest_loss=biggest_loss(original_trades, tick_value, commission),
                                        biggest_losing_streak=biggest_losing_streak(original_trades, tick_value, commission),
                                        patience_counter=0
                                    ))

        print(f"Generation #0")
        current_best_individual.print_parameters()
        print(f"Number of trades: {len(original_trades)}")
        print(f"Profit: {net_profit(original_trades, tick_value, commission)}")
        print("")

        generations_without_improvement = 0
        best_fitness = current_best_individual.fitness
        best_individual_so_far = current_best_individual

        for i in range(1, number_of_generations):

            population = make_new_population(train_df, population, fitness_function, tick_value, commission, maximum_holding_bars)

            current_best_individual = max(population, key=lambda individual: individual.fitness)

            if current_best_individual.fitness > best_fitness:
                best_fitness = current_best_individual.fitness
                generations_without_improvement = 0
                best_individual_so_far = current_best_individual
            else:
                generations_without_improvement += 1

            best_train_signal_df = generate_signals(train_df.copy(), best_individual_so_far)
            best_train_trades = backtester(best_train_signal_df, best_individual_so_far, maximum_holding_bars)

            generation_results.append(GenerationResult(
                                        window=window,
                                        generation=i,
                                        best_individual=best_individual_so_far,
                                        fitness=best_individual_so_far.fitness,
                                        number_of_trades=len(best_train_trades),
                                        net_profit=net_profit(best_train_trades, tick_value, commission),
                                        gross_profit=gross_profit(best_train_trades, tick_value, commission),
                                        gross_loss=gross_loss(best_train_trades, tick_value, commission),
                                        profit_factor=profit_factor(best_train_trades, tick_value, commission),
                                        max_drawdown=max_drawdown(best_train_trades, tick_value, commission),
                                        win_rate=win_rate(best_train_trades, tick_value, commission),
                                        average_trade=average_trade(best_train_trades, tick_value, commission),
                                        biggest_loss=biggest_loss(best_train_trades, tick_value, commission),
                                        biggest_losing_streak=biggest_losing_streak(best_train_trades, tick_value, commission),
                                        patience_counter=generations_without_improvement,
                                    ))

            if generations_without_improvement >= patience:

                print(f"Early stopping at generation #{i}")
                best_individual_so_far.print_parameters()
                print(f"Number of trades: {len(best_train_trades)}")
                print(f"Profit: {net_profit(best_train_trades, tick_value, commission)}")
                print("")
                
                break

            print(f"Generation #{i}")
            best_individual_so_far.print_parameters()
            print(f"Number of trades: {len(best_train_trades)}")
            print(f"Profit: {net_profit(best_train_trades, tick_value, commission)}")
            print("")
        
        best_individual_copy_for_test = copy_individual(best_individual_so_far)

        test_signal_df = generate_signals(test_df.copy(), best_individual_copy_for_test)

        test_trades = backtester(test_signal_df, best_individual_copy_for_test, maximum_holding_bars)

        test_fitness = fitness_function(test_trades, tick_value, commission)

        best_individual_copy_for_test.fitness = test_fitness

        walk_forward_results.append(WalkForwardResult(window = window, 
                                         best_individual = best_individual_so_far, 
                                         train_fitness = best_individual_so_far.fitness, 
                                         test_fitness = best_individual_copy_for_test.fitness))

        print(f"Best trained individual on test data:")
        best_individual_copy_for_test.print_parameters()
        print(f"Number of trades: {len(test_trades)}")
        print(f"Profit: {net_profit(test_trades, tick_value, commission)}")
        print("")
    
    return walk_forward_results, generation_results