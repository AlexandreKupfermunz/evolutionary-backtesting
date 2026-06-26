from data.data_loader import load_data
from src.trading.walk_forward import create_walk_forward_windows
from src.trading.walk_forward import run_walk_forward

from src.fitness.fitness_functions import basic_profit_fitness
from src.fitness.fitness_functions import profit_trade_fitness
from src.fitness.fitness_functions import basic_drawdown_fitness
from src.fitness.fitness_functions import drawdown_trade_fitness
from src.fitness.fitness_functions import complex_fitness


df = load_data("data/NQ-5D.txt", 50000)
windows = create_walk_forward_windows(len(df), 20000, 10000, 10000)
results = run_walk_forward(df, windows, 10, 20, basic_profit_fitness, 5, 4, 200,10)