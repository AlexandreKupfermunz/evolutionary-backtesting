def generate_signals(df, individual):
    
    df = add_imbalance_count_feature(df, individual.diagonal_imbalance_ratio_threshold)
    df = generate_long_signal(df, individual.min_impulse_candles, individual.max_duration_ms, individual.min_imbalance_count )
    df = generate_short_signal(df, individual.min_impulse_candles, individual.max_duration_ms, individual.min_imbalance_count )

    return df

# This part is to count the number of diagonal imbalances within the range of consecutive_up/down
def add_imbalance_count_feature(df, threshold):
    
    consecutive_up = df["consecutive_up"]
    consecutive_down = df["consecutive_down"]
    imbalance_ratio = df["diagonal_imbalance_ratio"]

    buy_imbalance_count_in_range = []
    sell_imbalance_count_in_range = []

    for i in range(len(df)):

        buy_imbalance_count = 0
        sell_imbalance_count = 0
        
        for j in range(int(consecutive_up.iloc[i])):
            
            if imbalance_ratio.iloc[i-j] > threshold:
                buy_imbalance_count += 1
            
        buy_imbalance_count_in_range.append(buy_imbalance_count)
        
        for j in range(int(consecutive_down.iloc[i])):
            
            if imbalance_ratio.iloc[i-j] < 1/threshold:
                sell_imbalance_count += 1
            
        sell_imbalance_count_in_range.append(sell_imbalance_count)

    df["buy_imbalance_count_in_range"] = buy_imbalance_count_in_range
    df["sell_imbalance_count_in_range"] = sell_imbalance_count_in_range

    return df

def generate_long_signal(df, min_impulse_candles, max_duration_ms, min_imbalance_count):

    consecutive_up = df["consecutive_up"] 
    impulse_duration = df["impulse_duration_ms"]
    long_imbalance_count_in_range = df["buy_imbalance_count_in_range"]

    long_signal = []

    for i in range(len(df)):
        if (consecutive_up.iloc[i] >= min_impulse_candles 
            and impulse_duration.iloc[i] <= max_duration_ms
            and long_imbalance_count_in_range.iloc[i] >= min_imbalance_count):
            long_signal.append(True)
        else:
            long_signal.append(False)
    
    df["long_signal"] = long_signal

    return df

def generate_short_signal(df, min_impulse_candles, max_duration_ms, min_imbalance_count):

    consecutive_down = df["consecutive_down"] 
    impulse_duration = df["impulse_duration_ms"]
    short_imbalance_count_in_range = df["sell_imbalance_count_in_range"]

    short_signal = []

    for i in range(len(df)):
        if (consecutive_down.iloc[i] >= min_impulse_candles 
            and impulse_duration.iloc[i] <= max_duration_ms
            and short_imbalance_count_in_range.iloc[i] >= min_imbalance_count):
            short_signal.append(True)
        else:
            short_signal.append(False)
    
    df["short_signal"] = short_signal

    return df