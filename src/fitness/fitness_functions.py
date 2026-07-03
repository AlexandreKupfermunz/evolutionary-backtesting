import math

def net_profit_fitness(performance_metrics):

    if performance_metrics.number_of_trades < 10:
        return -1000

    return performance_metrics.net_profit


def expectancy_fitness(performance_metrics):
    
    if performance_metrics.number_of_trades < 10:
        return -1000

    return performance_metrics.average_trade


def drawdown_adjusted_fitness(performance_metrics):

    if performance_metrics.number_of_trades < 10:
        return -1000

    profit = performance_metrics.net_profit
    drawdown = performance_metrics.max_drawdown

    fitness = profit / (1 + drawdown)

    return fitness

def balanced_fitness(performance_metrics):

    if performance_metrics.number_of_trades < 10:
        return -1000

    profit = performance_metrics.net_profit
    drawdown = performance_metrics.max_drawdown
    win_rate_ratio = performance_metrics.win_rate

    fitness = (profit*win_rate_ratio*math.sqrt(performance_metrics.number_of_trades))/(1+drawdown)

    return fitness


def robust_fitness(performance_metrics):

    if performance_metrics.number_of_trades < 10:
        return -1000

    profit = performance_metrics.net_profit
    drawdown = performance_metrics.max_drawdown
    win_rate_ratio = performance_metrics.win_rate
    losing_streak = performance_metrics.longest_losing_streak

    fitness = (profit*win_rate_ratio*math.sqrt(performance_metrics.number_of_trades))/((1 + drawdown)*math.sqrt(1 + losing_streak))

    return fitness