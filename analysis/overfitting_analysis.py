from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

RESULTS_FOLDER = Path("results")
OUTPUT_FOLDER = Path("analysis_output")

def create_train_test_fitness_df(generation_best_individuals_df, generation_column):
    """
    Creates one row per window and generation.

    It matches:
    - the train performance of the selected individual
    - the test performance of the same selected individual

    Then it calculates the generalization gap.
    """

    df = generation_best_individuals_df.copy()

    train_df = df[df["dataset_type"] == "train"].copy()
    test_df = df[df["dataset_type"] == "test"].copy()

    columns_to_keep = ["window_id", generation_column, "fitness"]

    train_df = train_df[columns_to_keep].rename(
        columns={"fitness": "train_fitness"}
    )

    test_df = test_df[columns_to_keep].rename(
        columns={"fitness": "test_fitness"}
    )

    merged_df = pd.merge(
        train_df,
        test_df,
        on=["window_id", generation_column],
        how="inner"
    )

    merged_df["generalization_gap"] = (
        merged_df["train_fitness"] - merged_df["test_fitness"]
    )

    return merged_df


def create_overfitting_summary_table(train_test_df, generation_column):
    """
    Creates one row per window.

    This table answers:
    Did train fitness improve while test fitness failed to improve?
    """

    df = train_test_df.copy()
    df = df.sort_values(["window_id", generation_column])

    summary_rows = []

    for window_id, group in df.groupby("window_id"):
        first_row = group.iloc[0]
        last_row = group.iloc[-1]

        train_improvement = (
            last_row["train_fitness"] - first_row["train_fitness"]
        )

        test_improvement = (
            last_row["test_fitness"] - first_row["test_fitness"]
        )

        gap_change = (
            last_row["generalization_gap"] - first_row["generalization_gap"]
        )

        row = {
            "window_id": window_id,

            "first_generation": first_row[generation_column],
            "last_generation": last_row[generation_column],

            "first_train_fitness": first_row["train_fitness"],
            "last_train_fitness": last_row["train_fitness"],
            "train_improvement": train_improvement,

            "first_test_fitness": first_row["test_fitness"],
            "last_test_fitness": last_row["test_fitness"],
            "test_improvement": test_improvement,

            "first_generalization_gap": first_row["generalization_gap"],
            "last_generalization_gap": last_row["generalization_gap"],
            "gap_change": gap_change,
        }

        row["overfit_flag"] = (
            train_improvement > 0
            and test_improvement <= 0
            and gap_change > 0
        )

        summary_rows.append(row)

    return pd.DataFrame(summary_rows)


def aggregate_by_generation(df, generation_column, metric_column):
    """
    Averages one metric across all windows for each generation.
    """

    grouped = (
        df.groupby(generation_column)[metric_column]
        .mean()
        .reset_index()
    )

    return grouped


def plot_train_vs_test_fitness(train_test_df, generation_column, output_path, title):
    """
    Plots average train fitness and average test fitness by generation.
    """

    train_grouped = aggregate_by_generation(
        train_test_df,
        generation_column,
        "train_fitness"
    )

    test_grouped = aggregate_by_generation(
        train_test_df,
        generation_column,
        "test_fitness"
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        train_grouped[generation_column],
        train_grouped["train_fitness"],
        label="Train fitness"
    )

    plt.plot(
        test_grouped[generation_column],
        test_grouped["test_fitness"],
        label="Test fitness"
    )

    plt.title(title)
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.legend()
      
    max_generation = int(test_grouped[generation_column].max())
    ticks = list(range(0, max_generation + 1, 5))
    plt.xticks(sorted(set(ticks)))

    plt.grid(True)

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()


def plot_generalization_gap(train_test_df, generation_column, output_path, title):
    """
    Plots the average generalization gap by generation.

    Generalization gap = train fitness - test fitness.
    """

    gap_grouped = aggregate_by_generation(
        train_test_df,
        generation_column,
        "generalization_gap"
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        gap_grouped[generation_column],
        gap_grouped["generalization_gap"],
        label="Generalization gap"
    )

    plt.axhline(0, linestyle="--")

    plt.title(title)
    plt.xlabel("Generation")
    plt.ylabel("Train fitness - test fitness")
    plt.legend()

    max_generation = int(gap_grouped[generation_column].max())
    ticks = list(range(0, max_generation + 1, 5))
    plt.xticks(sorted(set(ticks)))

    plt.grid(True)

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()


def run_current_best_overfitting_analysis(
    generation_best_individuals_path,
    output_folder_path
):
    """
    Overfitting analysis for the current best individual of each generation.

    This answers:
    Does the best individual of each generation overfit?
    """

    output_folder = Path(output_folder_path)
    output_folder.mkdir(parents=True, exist_ok=True)

    generation_best_individuals_df = pd.read_csv(generation_best_individuals_path)

    train_test_df = create_train_test_fitness_df(
        generation_best_individuals_df,
        generation_column="generation"
    )

    summary_table = create_overfitting_summary_table(
        train_test_df,
        generation_column="generation"
    )

    train_test_df.to_csv(
        output_folder / "current_best_train_test_fitness.csv",
        index=False
    )

    summary_table.to_csv(
        output_folder / "current_best_overfitting_summary.csv",
        index=False
    )

    plot_train_vs_test_fitness(
        train_test_df=train_test_df,
        generation_column="generation",
        output_path=output_folder / "current_best_train_vs_test_fitness.png",
        title="Current best train vs test fitness by generation"
    )

    plot_generalization_gap(
        train_test_df=train_test_df,
        generation_column="generation",
        output_path=output_folder / "current_best_generalization_gap.png",
        title="Current best generalization gap by generation"
    )

    return summary_table, train_test_df


def run_best_so_far_overfitting_analysis(
    best_so_far_path,
    output_folder_path
):
    """
    Overfitting analysis for the best-so-far individual.

    This answers:
    Does the optimizer's selected best-so-far strategy overfit?
    """

    output_folder = Path(output_folder_path)
    output_folder.mkdir(parents=True, exist_ok=True)

    best_so_far_df = pd.read_csv(best_so_far_path)

    train_test_df = create_train_test_fitness_df(
        best_so_far_df,
        generation_column="analysis_generation"
    )

    summary_table = create_overfitting_summary_table(
        train_test_df,
        generation_column="analysis_generation"
    )

    train_test_df.to_csv(
        output_folder / "best_so_far_train_test_fitness.csv",
        index=False
    )

    summary_table.to_csv(
        output_folder / "best_so_far_overfitting_summary.csv",
        index=False
    )

    plot_train_vs_test_fitness(
        train_test_df=train_test_df,
        generation_column="analysis_generation",
        output_path=output_folder / "best_so_far_train_vs_test_fitness.png",
        title="Best-so-far train vs test fitness by generation"
    )

    plot_generalization_gap(
        train_test_df=train_test_df,
        generation_column="analysis_generation",
        output_path=output_folder / "best_so_far_generalization_gap.png",
        title="Best-so-far generalization gap by generation"
    )

    return summary_table, train_test_df


def run_overfitting_analysis(
    generation_best_individuals_path,
    best_so_far_path,
    output_folder_path
):
    """
    Runs both overfitting analyses:
    1. Current best individual per generation
    2. Best-so-far individual per generation
    """

    output_folder = Path(output_folder_path)
    output_folder.mkdir(parents=True, exist_ok=True)

    current_best_output_folder = output_folder / "current_best"
    best_so_far_output_folder = output_folder / "best_so_far"

    current_best_summary, current_best_train_test_df = (
        run_current_best_overfitting_analysis(
            generation_best_individuals_path=generation_best_individuals_path,
            output_folder_path=current_best_output_folder
        )
    )

    best_so_far_summary, best_so_far_train_test_df = (
        run_best_so_far_overfitting_analysis(
            best_so_far_path=best_so_far_path,
            output_folder_path=best_so_far_output_folder
        )
    )

    return {
        "current_best_summary": current_best_summary,
        "current_best_train_test_df": current_best_train_test_df,
        "best_so_far_summary": best_so_far_summary,
        "best_so_far_train_test_df": best_so_far_train_test_df,
    }