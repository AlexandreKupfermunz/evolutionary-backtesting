from src.trading.data_loader import load_data
from src.trading.features import add_basic_features
from src.trading.strategy import generate_signals
from src.ga.individual import create_initial_population
from src.ga.evolution import make_new_population

NUMBERS_OF_GENERATIONS = 10

df = load_data("data/NQ-5D.txt", 20000)
df = add_basic_features(df)

population = create_initial_population(10, df)

best = max(population, key=lambda individual: individual.fitness)
print(best.fitness)

for i in range(NUMBERS_OF_GENERATIONS):

    population = make_new_population(population, df)

    best = max(population, key=lambda individual: individual.fitness)
    print(best.fitness)