class Trade: 
    
    def __init__(self, entry_index, exit_index, direction, entry_price, exit_price, exit_reason, entry_timestamp, exit_timestamp, result):
        self.entry_index = entry_index
        self.exit_index = exit_index
        self.direction = direction
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        self.entry_timestamp = entry_timestamp
        self.exit_timestamp = exit_timestamp
        self.result = result