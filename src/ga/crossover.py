from individual import copy 
import random

def crossover(individual_1, individual_2):

    random_number = random.randint(0,1)

    individual_copy = copy(individual_1)

    if (random_number == 1):
            individual_copy.min_impulse_candles = individual_2.min_impulse_candles

    random_number = random.randint(0,1)

    if (random_number == 1):
            individual_copy.max_duration_ms = individual_2.max_duration_ms
     
    random_number = random.randint(0,1)

    if (random_number == 1):
            individual_copy.diagonal_imbalance_ratio_threshold = individual_2.diagonal_imbalance_ratio_threshold
         
    random_number = random.randint(0,1)

    if (random_number == 1):
            individual_copy.min_imbalance_count = individual_2.min_imbalance_count

    random_number = random.randint(0,1)

    if (random_number == 1):
            individual_copy.take_profit_ticks = individual_2.take_profit_ticks
    
    random_number = random.randint(0,1)

    if (random_number == 1):
        individual_copy.stop_loss_ticks = individual_2.stop_loss_ticks

    if individual_copy.min_imbalance_count > individual_copy.min_impulse_candles:
        average = round(
            (individual_copy.min_imbalance_count + individual_copy.min_impulse_candles) / 2
        )

        individual_copy.min_impulse_candles = average
        individual_copy.min_imbalance_count = average

    return individual_copy