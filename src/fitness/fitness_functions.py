import math

def net_profit_fitness(performance_metrics):

    return performance_metrics.net_profit


def expectancy_fitness(performance_metrics):

    return performance_metrics.average_trade

def drawdown_adjusted_fitness(performance_metrics):

    profit = performance_metrics.net_profit
    max_drawdown = performance_metrics.max_drawdown
    number_of_trades = performance_metrics.number_of_trades

    if number_of_trades == 0:
        return -100

    fitness = (profit)/(number_of_trades * (1+max_drawdown))

    return fitness


def losing_streak_fitness(performance_metrics):

    profit = performance_metrics.net_profit
    losing_streak = performance_metrics.longest_losing_streak
    number_of_trades = performance_metrics.number_of_trades

    if number_of_trades == 0:
        return -100

    fitness = (profit) / (number_of_trades * (1 + losing_streak)) 

    return fitness