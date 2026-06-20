import pandas as pd

def add_basic_features(df):

    add_direction_features(df)
    add_volume_features(df)
    add_impulse_features(df)
    add_time_feature(df)

    return df


def add_direction_features(df):

    # This return true of false for each direction of the candles
    df["up"] = (df["Last"] > df["Last"].shift(1))
    df["down"] = (df["Last"] < df["Last"].shift(1))

    return df

def add_volume_features(df):

    # This replaces all 0s by 1s
    df["AskVolume"] = df["AskVolume"].replace(0,1)
    df["BidVolume"] = df["BidVolume"].replace(0,1)
    
    # This creates a the diagonal imbalance ratio 
    df["previous_bid"] = df["BidVolume"].shift(1)
    df["diagonal_imbalance_ratio"] = (df["AskVolume"]/df["previous_bid"])

    return df

def add_impulse_features(df):

    consecutive_up_count = 0
    consecutive_down_count = 0

    up = df["up"]
    down = df["down"]

    consecutive_up = []
    consecutive_down = []
    
    for i in range(len(up)):
        if up.iloc[i]:
            consecutive_down_count = 0
            consecutive_up_count += 1
            consecutive_up.append(consecutive_up_count)
            consecutive_down.append(consecutive_down_count)
        elif down.iloc[i]:
            consecutive_up_count = 0
            consecutive_down_count += 1
            consecutive_up.append(consecutive_up_count)
            consecutive_down.append(consecutive_down_count)
        else: 
            consecutive_up_count = 0
            consecutive_down_count = 0
            consecutive_up.append(consecutive_up_count)
            consecutive_down.append(consecutive_down_count)
        
    df["consecutive_up"] = consecutive_up
    df["consecutive_down"] = consecutive_down

    return df

def add_time_feature(df):

    df["timestamp"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    consecutive_up = df["consecutive_up"] 
    consecutive_down = df["consecutive_down"]
    timestamps = df["timestamp"]

    impulse_duration_ms = [] 

    for i in range(len(df)):

        n_up = consecutive_up.iloc[i]
        n_down = consecutive_down.iloc[i]

        if n_up > 0:
            start_index = i-(n_up-1)
            duration_ms = 1000*((timestamps.iloc[i]- timestamps.iloc[start_index]).total_seconds())
            impulse_duration_ms.append(duration_ms)
        
        elif n_down > 0:
            start_index = i-(n_down-1)
            duration_ms = 1000*((timestamps.iloc[i]- timestamps.iloc[start_index]).total_seconds())
            impulse_duration_ms.append(duration_ms)
        
        else:
            impulse_duration_ms.append(None)

    df["impulse_duration_ms"] = impulse_duration_ms

    return df