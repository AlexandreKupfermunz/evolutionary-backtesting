from trade import Trade

# TODO : hardcoded slippage for now
SLIPPAGE_TICKS = 1
TICK_SIZE = 0.25
slippage = SLIPPAGE_TICKS*TICK_SIZE 

MAXIMUM_HOLDING_BARS = 200

def backtester(df, individual):
    
    long_signal = df["long_signal"]
    short_signal = df["short_signal"]
    timestamp = df["timestamp"]
    last = df["Last"]
    high = df["High"]
    low = df["Low"]

    trades = []
    unclosed_trades = 0

    i = 0

    while i<len(df):

        if long_signal.iloc[i]:

            entry_price = last.iloc[i] + slippage
            take_profit_price = entry_price + individual.take_profit_ticks * TICK_SIZE
            raw_stop_loss_price = entry_price - individual.stop_loss_ticks * TICK_SIZE
            stop_loss_exit_price = raw_stop_loss_price - slippage

            trade_close = False

            for j in range(min(MAXIMUM_HOLDING_BARS, len(df) - i - 1)):

                if (low.iloc[i+j+1] <= raw_stop_loss_price):

                    result = stop_loss_exit_price - entry_price
                    result_ticks = result / TICK_SIZE
                    trades.append(Trade(i, i+j+1,"long", entry_price, stop_loss_exit_price, 
                                        "SL", timestamp.iloc[i] ,timestamp.iloc[i+j+1], result_ticks))
                    i = i+j+1
                    trade_close = True
                    break
                
                elif(high.iloc[i+j+1] >= take_profit_price):

                    result = take_profit_price - entry_price
                    result_ticks = result / TICK_SIZE
                    trades.append(Trade(i, i+j+1,"long", entry_price, take_profit_price, 
                                        "TP", timestamp.iloc[i], timestamp.iloc[i+j+1], result_ticks))
                    i = i+j+1
                    trade_close = True
                    break

            if not trade_close:
                i += 1
                unclosed_trades +=1
            
            

        elif short_signal.iloc[i]:
            
            entry_price = last.iloc[i] - slippage
            take_profit_price = entry_price - individual.take_profit_ticks * TICK_SIZE
            raw_stop_loss_price = entry_price + individual.stop_loss_ticks * TICK_SIZE
            stop_loss_exit_price = raw_stop_loss_price + slippage

            
            trade_close = False

            for j in range(min(MAXIMUM_HOLDING_BARS, len(df) - i - 1)):

                if(high.iloc[i+j+1] >= raw_stop_loss_price):

                    result = entry_price - stop_loss_exit_price
                    result_ticks = result / TICK_SIZE
                    trades.append(Trade(i, i+j+1,"short", entry_price, stop_loss_exit_price, 
                                        "SL", timestamp.iloc[i], timestamp.iloc[i+j+1], result_ticks))
                    i = i+j+1
                    trade_close = True
                    break
                
                elif(low.iloc[i+j+1] <= take_profit_price):

                    result = entry_price - take_profit_price
                    result_ticks = result / TICK_SIZE
                    trades.append(Trade(i, i+j+1,"short", entry_price, take_profit_price,
                                        "TP", timestamp.iloc[i], timestamp.iloc[i+j+1], result_ticks))
                    i = i+j+1
                    trade_close = True
                    break

            if not trade_close:
                i += 1
                unclosed_trades +=1

        else: 
            i += 1
    
    return trades, unclosed_trades