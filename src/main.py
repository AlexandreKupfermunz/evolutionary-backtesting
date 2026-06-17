from data_loader import load_data
from features import add_basic_features

df = load_data("data/EURUSD-10D.txt", nrows=100)
df = add_basic_features(df)

print(df.head())
print(df[["Last", "consecutive_up", "consecutive_down"]].head())