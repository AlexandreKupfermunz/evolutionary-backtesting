from src.trading.backtester import backtester

TICK_VALUE = 5
COMMISSION = 4

def setFitness(individual, trades):

    fitness = 0

    for trade in trades: 
        fitness += trade.result*TICK_VALUE - COMMISSION

    if len(trades) < 10:
        fitness -= 1000

    individual.fitness = fitness

    return fitness