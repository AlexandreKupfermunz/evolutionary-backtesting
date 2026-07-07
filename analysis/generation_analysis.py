import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def run_generation_learning_analysis(generation_results_path, generation_best_individuals_path, output_folder_path):

    output_folder = Path(output_folder_path)
    output_folder.mkdir(parents=True, exist_ok=True)

    generation_results_df = pd.read_csv(generation_results_path)
    generation_best_individuals_df = pd.read_csv(generation_best_individuals_path)

    best_so_far_df = create_best_so_far_df(generation_best_individuals_df)

    summary_table = create_learning_summary_table(
        generation_results_df,
        best_so_far_df
    )

    best_so_far_df.to_csv(output_folder / "best_so_far.csv", index=False)
    summary_table.to_csv(output_folder / "generation_learning_summary.csv", index=False)

    plot_population_average_fitness(generation_results_df, output_folder)
    plot_population_best_fitness(generation_results_df, output_folder)
    plot_population_std_fitness(generation_results_df, output_folder)
    plot_population_fitness_range(generation_results_df, output_folder)
    plot_best_so_far_train_fitness(best_so_far_df, output_folder)
    plot_selected_generation(best_so_far_df, output_folder)

    return summary_table, best_so_far_df

def create_best_so_far_df(generation_best_individuals_df):

    df = generation_best_individuals_df.copy()

    df = df.sort_values(["window_id", "generation"])

    train_df = df[df["dataset_type"] == "train"].copy()
    test_df = df[df["dataset_type"] == "test"].copy()

    best_so_far_rows = []

    for window_id, train_group in train_df.groupby("window_id"):
        test_group = test_df[test_df["window_id"] == window_id]

        best_generation_so_far = None
        best_fitness_so_far = None

        for _, train_row in train_group.iterrows():
            generation = train_row["generation"]
            current_train_fitness = train_row["fitness"]

            if best_fitness_so_far is None or current_train_fitness > best_fitness_so_far:
                best_fitness_so_far = current_train_fitness
                best_generation_so_far = generation

            selected_train_row = train_group[
                train_group["generation"] == best_generation_so_far
            ].iloc[0].copy()

            selected_test_row = test_group[
                test_group["generation"] == best_generation_so_far
            ].iloc[0].copy()

            selected_train_row["analysis_generation"] = generation
            selected_test_row["analysis_generation"] = generation

            selected_train_row["selected_generation"] = best_generation_so_far
            selected_test_row["selected_generation"] = best_generation_so_far

            best_so_far_rows.append(selected_train_row)
            best_so_far_rows.append(selected_test_row)

    return pd.DataFrame(best_so_far_rows)

def create_learning_summary_table(generation_results_df, best_so_far_df):

    population_df = generation_results_df.copy()
    best_df = best_so_far_df.copy()

    population_df = population_df.sort_values(["window_id", "generation"])
    best_df = best_df[best_df["dataset_type"] == "train"].copy()
    best_df = best_df.sort_values(["window_id", "analysis_generation"])

    summary_rows = []

    for window_id, group in population_df.groupby("window_id"):
        first_row = group.iloc[0]
        last_row = group.iloc[-1]

        best_group = best_df[best_df["window_id"] == window_id]

        if best_group.empty:
            continue

        first_best_so_far = best_group.iloc[0]
        last_best_so_far = best_group.iloc[-1]

        row = {
            "window_id": window_id,

            "first_generation": first_row["generation"],
            "last_generation": last_row["generation"],

            "first_population_best_fitness": first_row["best_fitness"],
            "last_population_best_fitness": last_row["best_fitness"],
            "population_best_improvement": last_row["best_fitness"] - first_row["best_fitness"],

            "first_population_average_fitness": first_row["average_fitness"],
            "last_population_average_fitness": last_row["average_fitness"],
            "population_average_improvement": last_row["average_fitness"] - first_row["average_fitness"],

            "first_population_median_fitness": first_row["median_fitness"],
            "last_population_median_fitness": last_row["median_fitness"],
            "population_median_improvement": last_row["median_fitness"] - first_row["median_fitness"],

            "first_std_fitness": first_row["std_fitness"],
            "last_std_fitness": last_row["std_fitness"],
            "std_change": last_row["std_fitness"] - first_row["std_fitness"],

            "first_fitness_range": first_row["fitness_range"],
            "last_fitness_range": last_row["fitness_range"],
            "fitness_range_change": last_row["fitness_range"] - first_row["fitness_range"],

            "first_best_so_far_fitness": first_best_so_far["fitness"],
            "last_best_so_far_fitness": last_best_so_far["fitness"],
            "best_so_far_improvement": last_best_so_far["fitness"] - first_best_so_far["fitness"],

            "final_selected_generation": last_best_so_far["selected_generation"],
        }

        row["optimizer_learned"] = (
            row["population_average_improvement"] > 0
            and row["best_so_far_improvement"] > 0
        )

        summary_rows.append(row)

    return pd.DataFrame(summary_rows)


def aggregate_by_generation(df, generation_column, metric_column):

    grouped = (
        df.groupby(generation_column)[metric_column]
        .mean()
        .reset_index()
    )

    return grouped


def plot_metric_by_generation(df, generation_column, metric_column, title, ylabel, output_path, show_std=False):

    plt.figure(figsize=(10, 6))

    if show_std:
        grouped = (
            df.groupby(generation_column)[metric_column]
            .agg(["mean", "std"])
            .reset_index()
        )

        plt.plot(
            grouped[generation_column],
            grouped["mean"],
            label="Mean",
            linewidth=2
        )

        plt.fill_between(
            grouped[generation_column],
            grouped["mean"] - grouped["std"],
            grouped["mean"] + grouped["std"],
            alpha=0.2,
            label="±1 std"
        )

    else:
        grouped = (
            df.groupby(generation_column)[metric_column]
            .mean()
            .reset_index()
        )

        plt.plot(
            grouped[generation_column],
            grouped[metric_column],
            linewidth=2
        )

    plt.title(title)
    plt.xlabel("Generation")
    plt.ylabel(ylabel)

    if show_std:
        plt.legend()

    plt.grid(alpha=0.3)

    max_generation = int(grouped[generation_column].max())
    ticks = list(range(0, max_generation + 1, 5))
    plt.xticks(sorted(set(ticks)))

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

def plot_population_average_fitness(generation_results_df, output_folder):

    plot_metric_by_generation(
        df=generation_results_df,
        generation_column="generation",
        metric_column="average_fitness",
        title="Population average fitness by generation",
        ylabel="Average fitness",
        output_path=output_folder / "population_average_fitness.png",
        show_std=True,
    )


def plot_population_best_fitness(generation_results_df, output_folder):

    plot_metric_by_generation(
        df=generation_results_df,
        generation_column="generation",
        metric_column="best_fitness",
        title="Population best fitness by generation",
        ylabel="Best fitness",
        output_path=output_folder / "population_best_fitness.png"
    )


def plot_population_std_fitness(generation_results_df, output_folder):

    plot_metric_by_generation(
        df=generation_results_df,
        generation_column="generation",
        metric_column="std_fitness",
        title="Population fitness standard deviation by generation",
        ylabel="Fitness standard deviation",
        output_path=output_folder / "population_std_fitness.png"
    )


def plot_population_fitness_range(generation_results_df, output_folder):

    plot_metric_by_generation(
        df=generation_results_df,
        generation_column="generation",
        metric_column="fitness_range",
        title="Population fitness range by generation",
        ylabel="Fitness range",
        output_path=output_folder / "population_fitness_range.png"
    )


def plot_best_so_far_train_fitness(best_so_far_df, output_folder):

    train_df = best_so_far_df[best_so_far_df["dataset_type"] == "train"].copy()

    plot_metric_by_generation(
        df=train_df,
        generation_column="analysis_generation",
        metric_column="fitness",
        title="Best-so-far train fitness by generation",
        ylabel="Best-so-far train fitness",
        output_path=output_folder / "best_so_far_train_fitness.png"
    )


def plot_selected_generation(best_so_far_df, output_folder):

    train_df = best_so_far_df[best_so_far_df["dataset_type"] == "train"].copy()

    plot_metric_by_generation(
        df=train_df,
        generation_column="analysis_generation",
        metric_column="selected_generation",
        title="Selected generation by analysis generation",
        ylabel="Selected generation",
        output_path=output_folder / "selected_generation.png"
    )