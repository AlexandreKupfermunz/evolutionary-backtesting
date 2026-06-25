from data.data_loader import load_data
from features.impulse_strategy_features import add_impulse_strategy_features
from src.ga.individual import create_initial_population
from src.ga.evolution import make_new_population

class WalkForwardWindow:

    def __init__(self, train_start, train_end, test_start, test_end):
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start
        self.test_end = test_end

def create_walk_forward_windows(df_length, train_size, test_size, step_size):

    windows = []

    number_of_windows = ((df_length - train_size - test_size) // step_size) + 1
    
    for i in range(number_of_windows):

        train_start =  i * step_size
        train_end  = train_size + i * step_size 
        test_start = train_size + i * step_size 
        test_end = train_size + test_size + i * step_size

        windows.append(WalkForwardWindow(train_start, train_end, test_start, test_end))

    return windows 


