from strategies.impulse_strategy.impulse_strategy_signals import generate_impulse_signals
from src.fitness.fitness_metrics import calculate_fitness_metrics
from src.trading.backtester import backtester

def evaluate_individual_on_df(df, individual, generate_strategy_signals, fitness_function, tick_value, commission, maximum_holding_bars):
    
    signal_df = generate_strategy_signals(df.copy(), individual)
    trades = backtester(signal_df, individual, maximum_holding_bars)
    fitness_metrics = calculate_fitness_metrics(trades, tick_value, commission)
    fitness = fitness_function(fitness_metrics)

    return trades, fitness
