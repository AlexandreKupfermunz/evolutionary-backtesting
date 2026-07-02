def net_profit(trades, tick_value, commission):

    net_profit = 0

    for trade in trades: 
        net_profit += trade_profit(trade, tick_value, commission)

    return net_profit

def gross_profit(trades, tick_value, commission):

    gross_profit = 0

    for trade in trades:

        single_trade_profit  = trade_profit(trade, tick_value, commission)

        if single_trade_profit  > 0:
            gross_profit += single_trade_profit 

    return gross_profit
 
def gross_loss(trades, tick_value, commission): 

    gross_loss = 0 

    for trade in trades:

        single_trade_profit = trade_profit(trade, tick_value, commission)

        if single_trade_profit < 0:
            gross_loss += abs(single_trade_profit)

    return gross_loss

def biggest_losing_streak(trades, tick_value, commission):

    losing_count = 0 
    max_losing_count = 0

    for trade in trades:

        single_trade_profit  = trade_profit(trade, tick_value, commission)

        if single_trade_profit < 0:
            losing_count +=1
        else: 
            losing_count = 0
        
        if losing_count > max_losing_count:
            max_losing_count = losing_count
    
    return max_losing_count

def profit_factor(trades, tick_value, commission):

    gross_profit_value = gross_profit(trades, tick_value, commission)
    gross_loss_value = gross_loss(trades, tick_value, commission)
    
    if len(trades) == 0:
        return None

    gross_profit_value = gross_profit(trades, tick_value, commission)
    gross_loss_value = gross_loss(trades, tick_value, commission)

    if gross_loss_value == 0:
        return float("inf")

    profit_factor = gross_profit_value/gross_loss_value

    return profit_factor

def max_drawdown(trades, tick_value, commission):

    equity = 0
    highest_equity = 0
    max_drawdown = 0

    for trade in trades:

        single_trade_profit  = trade_profit(trade, tick_value, commission)

        equity += single_trade_profit 

        if equity > highest_equity:
            highest_equity = equity

        current_drawdown = highest_equity - equity

        if current_drawdown > max_drawdown:
            max_drawdown = current_drawdown

    return max_drawdown

def win_rate(trades, tick_value, commission):
    
    if len(trades) == 0:
        return None

    win_count = 0

    for trade in trades:
        single_trade_profit = trade_profit(trade, tick_value, commission)

        if single_trade_profit > 0:
            win_count += 1

    return win_count / len(trades)

def average_trade(trades, tick_value, commission):

    if len(trades) == 0: 
        return 0
    
    total_profit = 0

    for trade in trades:
        total_profit += trade_profit(trade, tick_value, commission)
    
    average = total_profit / len(trades)

    return average

def biggest_loss(trades, tick_value, commission):

    biggest_loss = 0

    for trade in trades:
        single_trade_profit = trade_profit(trade, tick_value, commission)

        if single_trade_profit < 0:
            loss = abs(single_trade_profit)

            if loss > biggest_loss:
                biggest_loss = loss

    return biggest_loss

def trade_profit(trade, tick_value, commission):
    
    return trade.result * tick_value - commission