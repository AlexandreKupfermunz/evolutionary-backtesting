class Individual:

    def __init__(self, impulse_candles, max_duration_ms, take_profit_ticks, 
                 stop_loss_ticks, diagonal_imbalance_ratio_threshold, min_imbalance_count):
        
        self.impulse_candles = impulse_candles
        self.max_duration_ms = max_duration_ms
        self.take_profit_ticks = take_profit_ticks
        self.stop_loss_ticks = stop_loss_ticks
        self.diagonal_imbalance_ratio_threshold = diagonal_imbalance_ratio_threshold
        self.min_imbalance_count = min_imbalance_count
        self.fitness = 0

    def print_parameters(self):

        print(f"Impulse Candles: {self.impulse_candles}")
        print(f"Max duration: {self.max_duration_ms} ms")
        print(f" Take profit: {self.take_profit_ticks} ticks")
        print(f"Stop loss: {self.stop_loss_ticks} ticks")
        print(f"Imbalance ratio threshold: {self.diagonal_imbalance_ratio_threshold}")
        print(f"Min numbers of imbalances: {self.min_imbalance_count}")
        print(f"Fitness : {self.fitness}")