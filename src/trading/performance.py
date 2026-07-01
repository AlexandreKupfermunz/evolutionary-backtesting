from src.fitness.metrics import net_profit
from src.fitness.metrics import gross_profit
from src.fitness.metrics import gross_loss
from src.fitness.metrics import biggest_losing_streak
from src.fitness.metrics import profit_factor
from src.fitness.metrics import max_drawdown
from src.fitness.metrics import win_rate
from src.fitness.metrics import average_trade
from src.fitness.metrics import biggest_loss

class PerformanceMetrics:

    def __init__(
        self,
        number_of_trades,
        net_profit,
        gross_profit,
        gross_loss,
        profit_factor,
        max_drawdown,
        win_rate,
        average_trade,
        biggest_loss,
        biggest_losing_streak,
    ):
        self.number_of_trades = number_of_trades
        self.net_profit = net_profit
        self.gross_profit = gross_profit
        self.gross_loss = gross_loss
        self.profit_factor = profit_factor
        self.max_drawdown = max_drawdown
        self.win_rate = win_rate
        self.average_trade = average_trade
        self.biggest_loss = biggest_loss
        self.biggest_losing_streak = biggest_losing_streak

    def to_dict(self):

        return({
            "numbers_of_trades": self.number_of_trades,
            "net_profit": self.net_profit,
            "gross_profit": self.gross_profit,
            "gross_loss": self.gross_loss,
            "profit_factor":self.profit_factor,
            "max_drawdown": self.max_drawdown,
            "win_rate": self.win_rate,
            "average_trade": self.average_trade,
            "biggest_lost": self.biggest_loss,
            "biggest_losing_streak": self.biggest_losing_streak
        })
    
def calculate_performance_metrics(trades, tick_value, commission):
    return PerformanceMetrics(
        number_of_trades=len(trades),
        net_profit=net_profit(trades, tick_value, commission),
        gross_profit=gross_profit(trades, tick_value, commission),
        gross_loss=gross_loss(trades, tick_value, commission),
        profit_factor=profit_factor(trades, tick_value, commission),
        max_drawdown=max_drawdown(trades, tick_value, commission),
        win_rate=win_rate(trades, tick_value, commission),
        average_trade=average_trade(trades, tick_value, commission),
        biggest_loss=biggest_loss(trades, tick_value, commission),
        biggest_losing_streak=biggest_losing_streak(trades, tick_value, commission),
    )