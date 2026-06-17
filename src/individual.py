class Individual:

    def __init__(self, impulse_candles, max_duration_ms, take_profit_ticks, 
                 stop_loss_ticks, min_imbalances):
        self.impulse_candles = impulse_candles
        self.max_duration_ms = max_duration_ms
        self.take_profit_ticks = take_profit_ticks
        self.stop_loss_ticks = stop_loss_ticks
        self.min_imbalances = min_imbalances
        self.fitness = 0

    def print_parameters(self):
        print(f"Impulse Candles: {self.impulse_candles}")
        print(f"Max duration: {self.max_duration_ms} ms")
        print(f" Take profit: {self.take_profit_ticks} ticks")
        print(f"Stop loss: {self.stop_loss_ticks} ticks")
        print(f"Min imbalances: {self.min_imbalances}")
        print(f"Fitness : {self.fitness}")