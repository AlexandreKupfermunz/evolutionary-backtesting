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


def basic_profit_fitness(trades, tick_value, commission):
        
    net_profit_value = net_profit(trades, tick_value, commission)
    numbers_of_trades = len(trades)

    if numbers_of_trades < 10:
        return -1000

    fitness = net_profit_value

    return fitness
    
def profit_trade_fitness(trades, tick_value, commission):
        
    net_profit_value = net_profit(trades, tick_value, commission)
    numbers_of_trades = len(trades)

    if numbers_of_trades < 10:
        return -1000

    fitness = net_profit_value* math.sqrt(numbers_of_trades)

    return fitness
    
def basic_drawdown_fitness(trades, tick_value, commission):

    net_profit_value = net_profit(trades, tick_value, commission)
    max_drawdown_value = max_drawdown(trades, tick_value, commission)
    numbers_of_trades = len(trades)

    if numbers_of_trades < 10:
        return -1000

    fitness = (net_profit_value)/(1+max_drawdown_value)

    return fitness
    
def drawdown_trade_fitness(trades, tick_value, commission):

    net_profit_value = net_profit(trades, tick_value, commission)
    max_drawdown_value = max_drawdown(trades, tick_value, commission)
    numbers_of_trades = len(trades)

    if numbers_of_trades < 10:
        return -1000

    fitness = (net_profit_value*math.sqrt(numbers_of_trades))/(1+max_drawdown_value)

    return fitness
    
def complex_fitness(trades, tick_value, commission):

    net_profit_value = net_profit(trades, tick_value, commission)
    max_drawdown_value = max_drawdown(trades, tick_value, commission)
    win_rate_ratio = win_rate(trades, tick_value, commission)
    losing_streak = biggest_losing_streak(trades, tick_value, commission)
    numbers_of_trades = len(trades)

    fitness = (net_profit_value*win_rate_ratio*math.sqrt(numbers_of_trades))/((1+max_drawdown_value)*(1+losing_streak))
        
    return fitness