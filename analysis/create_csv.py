import pandas as pd

def create_csv(walk_forward_results, walk_forward_trades, generation_results, generation_best_individuals, folder):

    walk_forward_df = pd.DataFrame(
        [result.to_dict() for result in walk_forward_results]
    )

    walk_forward_trades_df = pd.DataFrame(
        [trade.to_dict() for trade in walk_forward_trades ]
    )

    generation_results_df = pd.DataFrame(
        [result.to_dict() for result in generation_results]
    )

    generation_best_individuals_df = pd.DataFrame(
        [result.to_dict() for result in generation_best_individuals]
    )

    walk_forward_csv = folder / "walk_forward_results.csv"
    walk_forward_trades_csv = folder / "walk_forward_trades.csv"
    generation_results_csv = folder / "generation_results.csv"
    generation_best_individuals_csv = folder / "generation_individuals.csv"


    walk_forward_df.to_csv(walk_forward_csv, index=False)
    walk_forward_trades_df.to_csv(walk_forward_trades_csv, index = False)
    generation_results_df.to_csv(generation_results_csv, index=False)
    generation_best_individuals_df.to_csv(generation_best_individuals_csv, index=False)
