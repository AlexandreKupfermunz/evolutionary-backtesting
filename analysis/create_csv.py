import pandas as pd

def create_csv(walk_forward_results, generation_train_results, generation_test_results, walk_forward_trades, generation_test_trades, folder):

    walk_forward_df = pd.DataFrame(
        [result.to_dict() for result in walk_forward_results]
    )

    generation_train_df = pd.DataFrame(
        [result.to_dict() for result in generation_train_results]
    )

    generation_test_df = pd.DataFrame(
        [result.to_dict() for result in generation_test_results]
    )

    walk_forward_trades_df = pd.DataFrame(
        [trade.to_dict() for trade in walk_forward_trades ]
    )

    generation_test_trades_df = pd.DataFrame(
        [trade.to_dict() for trade in generation_test_trades ]
    )

    walk_forward_csv = folder / "walk_forward_results.csv"
    generation_train_csv = folder / "generation_train_results.csv"
    generation_test_csv = folder / "generation_test_results.csv"
    walk_forward_trades_csv = folder / "walk_forward_trades.csv"
    generation_test_trades_csv = folder / "generation_test_trades.csv"

    walk_forward_df.to_csv(walk_forward_csv, index=False)
    generation_train_df.to_csv(generation_train_csv, index=False)
    generation_test_df.to_csv(generation_test_csv, index=False)
    walk_forward_trades_df.to_csv(walk_forward_trades_csv, index = False)
    generation_test_trades_df.to_csv(generation_test_trades_csv, index = False)
