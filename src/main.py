from data.data_loader import load_data
from src.trading.walk_forward import create_walk_forward_windows
from src.trading.walk_forward import run_walk_forward


df = load_data("data/NQ-5D.txt", 50000)
windows = create_walk_forward_windows(len(df), 20000, 10000, 10000)
results = run_walk_forward(df, windows, 10, 20, 200)