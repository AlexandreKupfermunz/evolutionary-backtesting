from src.fitness.metrics import net_profit

def basic_profit_set_fitness(individual, trades):

    fitness = net_profit(trades)

    if len(trades) < 10:
        fitness -= 1000

    individual.fitness = fitness

    return fitness