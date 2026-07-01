from src.strategies.impulse_strategy import generate_signals
from src.trading.backtester import backtester

def evaluate_individual_on_df(df, individual, fitness_function, tick_value, commission, maximum_holding_bars):
    
    signal_df = generate_signals(df.copy(), individual)
    trades = backtester(signal_df, individual, maximum_holding_bars)
    fitness = fitness_function(trades, tick_value, commission)

    return trades, fitness
