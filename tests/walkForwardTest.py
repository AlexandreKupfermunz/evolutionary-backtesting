from data.data_loader import load_data
from src.trading.walk_forward import create_rolling_walk_forward_windows
from src.trading.walk_forward import run_walk_forward

from src.fitness.fitness_functions import basic_profit_fitness
from src.fitness.fitness_functions import profit_trade_fitness
from src.fitness.fitness_functions import basic_drawdown_fitness
from src.fitness.fitness_functions import drawdown_trade_fitness
from src.fitness.fitness_functions import complex_fitness


df = load_data("data/NQ-Sample_Data.txt", 5000)
windows = create_rolling_walk_forward_windows(len(df), 2000, 1000, 1000)
results = run_walk_forward(df, windows, 10, 20, basic_profit_fitness, 5, 4, 200, 5)