from data.data_loader import load_data
from features.impultion_strategy_features import add_impulsion_strategy_features
from src.ga.individual import create_initial_population
from src.ga.evolution import make_new_population

NUMBERS_OF_GENERATIONS = 2

df = load_data("data/NQ-5D.txt", 20000)
df = add_impulsion_strategy_features(df)

population = create_initial_population(10, df)

best = max(population, key=lambda individual: individual.fitness)

print(f"Generation #0")
best.print_parameters()
print("")

for i in range(NUMBERS_OF_GENERATIONS):

    population = make_new_population(population, df)

    best = max(population, key=lambda individual: individual.fitness)

    print(f"Generation #{i+1}")
    best.print_parameters()
    print("")