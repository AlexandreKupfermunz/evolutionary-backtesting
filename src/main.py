import src.trading.data_loader
import src.trading.features
import src.ga.individual

df = src.trading.data_loader.load_data("data/NQ-5D.txt", nrows=100)
df = src.trading.features.add_basic_features(df)

print(df[[
    "Last",
    "up",
    "down",
    "consecutive_up",
    "consecutive_down",
    "impulse_duration_ms"
]].head(60))