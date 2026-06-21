from src.trading.data_loader import load_data
from src.trading.features import add_basic_features

df = load_data("data/EURUSD-10D.txt", nrows=100)
df = add_basic_features(df)

print(df[[
    "Last",
    "up",
    "down",
    "consecutive_up",
    "consecutive_down",
    "impulse_duration_ms"
]].head(60))