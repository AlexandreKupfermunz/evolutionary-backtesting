from src.trading.data_loader import load_data
from src.trading.backtester import backtester

TICK_VALUE = 5
COMMISSION = 4

df = load_data("tests/deterministic_50_rows.csv")

def setFitness(individual):

    trades = backtester(df, individual, 200)

    fitness = 0

    for trade in trades: 
        fitness += trade.result*TICK_VALUE - COMMISSION

    if len(trades) < 10:
        fitness -= 1000

    individual.fitness = fitness

    return fitness

