import pandas as pd

def filter_trading_hours(df, sessions):

    df = df.copy()

    df["Time"] = pd.to_datetime(df["Time"],format="mixed").dt.time

    candles = []

    for start_time, end_time in sessions:

        session = df[(df["Time"] >= start_time) & (df["Time"] <= end_time)]

        candles.append(session)

    df = pd.concat(candles)

    return df