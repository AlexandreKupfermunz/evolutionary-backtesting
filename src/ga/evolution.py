from src.trading.backtester import backtester
from src.strategies.impulse_strategy import generate_impulse_signals
from src.ga.selection import selection
from src.ga.crossover import crossover
from src.ga.mutation import mutation
from src.fitness.performance import calculate_performance_metrics

def make_new_population(df, population, fitness_function, tick_value, commission, maximum_holding_bars):

    new_population = []

    for _ in population:

        parent_1 = selection(population)
        parent_2 = selection(population)

        while(parent_1 == parent_2):
            parent_2 = selection(population)
        
        child = crossover(parent_1, parent_2)

        child = mutation(child)

        new_population.append(child)

    for individual in new_population:

        signal_df = generate_impulse_signals(df, individual)
        
        trades = backtester(signal_df, individual, maximum_holding_bars)

        performance_metrics = calculate_performance_metrics(trades, tick_value, commission)
        fitness = fitness_function(performance_metrics)

        individual.fitness = fitness

    return new_population