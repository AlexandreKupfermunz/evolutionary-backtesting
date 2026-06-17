def add_basic_features(df):

    add_direction_features(df)
    add_volume_features(df)

    return df

def add_direction_features(df):
    # This return true of false for each direction of the candles
    df["up"] = (df["Last"] > df["Last"].shift(1))
    df["down"] = (df["Last"] < df["Last"].shift(1))

    df["consecutive_up"] = 0
    df["consecutive_down"] = 0
    count_up = 0
    count_down = 0
    for i in range(len(df["consecutive_up"])):
        if df.loc[i, "up"] == True:
            count_up = count_up + 1
            df.loc[i, "consecutive_up"] = count_up
        else:
            count_up = 0
            df.loc[i, "consecutive_up"] = count_up
    
    for i in range(len(df["consecutive_down"])):
        if df.loc[i, "down"] == True:
            count_down = count_down + 1
            df.loc[i, "consecutive_down"] = count_down
        else:
            count_down = 0
            df.loc[i, "consecutive_down"] = count_down

    return df

def add_volume_features(df):

    # This replaces all 0s by 1s
    df["AskVolume"] = df["AskVolume"].replace(0,1)
    df["BidVolume"] = df["BidVolume"].replace(0,1)

    # This creates a the diagonal imbalance ratio 
    df["previous_bid"] = df["BidVolume"].shift(1)
    df["diagonal_imbalance_ratio"] = (df["AskVolume"]/df["previous_bid"])

    return df