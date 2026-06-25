from src.trading.backtester import backtester
from strategies.impulse_strategy import generate_signals
from src.ga.fitness import set_fitness
from src.ga.selection import selection
from src.ga.crossover import crossover
from src.ga.mutation import mutation

def make_new_population(df, population, maximum_holding_bars):

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

        df = generate_signals(df, individual)
        
        trades = backtester(df, individual, maximum_holding_bars)
        set_fitness(individual, trades)

    return new_population