from src.fitness.metrics import net_profit
from src.fitness.metrics import gross_profit
from src.fitness.metrics import gross_loss
from src.fitness.metrics import biggest_losing_streak
from src.fitness.metrics import profit_factor
from src.fitness.metrics import max_drawdown
from src.fitness.metrics import win_rate
from src.fitness.metrics import average_trade
from src.fitness.metrics import biggest_loss

import math

def net_profit_fitness(trades, tick_value, commission):

    number_of_trades = len(trades)

    if number_of_trades < 10:
        return -1000

    return net_profit(trades, tick_value, commission)


def expectancy_fitness(trades, tick_value, commission):

    number_of_trades = len(trades)
    
    if number_of_trades < 10:
        return -1000

    return average_trade(trades, tick_value, commission)


def drawdown_adjusted_fitness(trades, tick_value, commission):

    number_of_trades = len(trades)

    if number_of_trades < 10:
        return -1000

    profit = net_profit(trades, tick_value, commission)
    drawdown = max_drawdown(trades, tick_value, commission)

    fitness = profit / (1 + drawdown)

    return fitness


def balanced_fitness(trades, tick_value, commission):

    number_of_trades = len(trades)

    if number_of_trades < 10:
        return -1000

    profit = net_profit(trades, tick_value, commission)
    drawdown = max_drawdown(trades, tick_value, commission)
    win_rate_ratio = win_rate(trades, tick_value, commission)

    fitness = (profit*win_rate_ratio*math.sqrt(number_of_trades))/(1+drawdown)

    return fitness


def robust_fitness(trades, tick_value, commission):

    number_of_trades = len(trades)

    if number_of_trades < 10:
        return -1000

    profit = net_profit(trades, tick_value, commission)
    drawdown = max_drawdown(trades, tick_value, commission)
    win_rate_ratio = win_rate(trades, tick_value, commission)
    losing_streak = biggest_losing_streak(trades, tick_value, commission)

    fitness = (profit*win_rate_ratio*math.sqrt(number_of_trades))/((1 + drawdown)*math.sqrt(1 + losing_streak))

    return fitness