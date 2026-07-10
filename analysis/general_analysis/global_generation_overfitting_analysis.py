from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from analysis.general_analysis.generation_analysis import create_best_so_far_df
from analysis.general_analysis.overfitting_analysis import create_train_test_fitness_df


def load_all_generation_files(results_folder_path):
    results_folder = Path(results_folder_path)

    generation_results_rows = []
    generation_best_individuals_rows = []

    for walk_forward_folder in results_folder.iterdir():
        if not walk_forward_folder.is_dir():
            continue

        walk_forward_type = walk_forward_folder.name

        if walk_forward_type not in ["rolling", "expanding"]:
            continue

        for fitness_folder in walk_forward_folder.iterdir():
            if not fitness_folder.is_dir():
                continue

            fitness_function = fitness_folder.name

            if walk_forward_type == "rolling":
                for train_size_folder in fitness_folder.iterdir():
                    if not train_size_folder.is_dir():
                        continue

                    train_size = train_size_folder.name

                    for repetition_folder in train_size_folder.iterdir():
                        if not repetition_folder.is_dir():
                            continue

                        add_generation_files(
                            repetition_folder,
                            generation_results_rows,
                            generation_best_individuals_rows,
                            walk_forward_type,
                            fitness_function,
                            train_size,
                            repetition_folder.name
                        )

            elif walk_forward_type == "expanding":
                for repetition_folder in fitness_folder.iterdir():
                    if not repetition_folder.is_dir():
                        continue

                    add_generation_files(
                        repetition_folder,
                        generation_results_rows,
                        generation_best_individuals_rows,
                        walk_forward_type,
                        fitness_function,
                        "expanding",
                        repetition_folder.name
                    )

    generation_results_df = pd.concat(
        generation_results_rows,
        ignore_index=True
    ) if generation_results_rows else pd.DataFrame()

    generation_best_individuals_df = pd.concat(
        generation_best_individuals_rows,
        ignore_index=True
    ) if generation_best_individuals_rows else pd.DataFrame()

    return generation_results_df, generation_best_individuals_df


def add_generation_files(
    repetition_folder,
    generation_results_rows,
    generation_best_individuals_rows,
    walk_forward_type,
    fitness_function,
    train_size,
    repetition
):
    generation_results_path = repetition_folder / "generation_results.csv"
    generation_best_individuals_path = repetition_folder / "generation_best_individuals.csv"

    if generation_results_path.exists():
        df = pd.read_csv(generation_results_path)
        add_metadata(df, walk_forward_type, fitness_function, train_size, repetition)
        generation_results_rows.append(df)

    if generation_best_individuals_path.exists():
        df = pd.read_csv(generation_best_individuals_path)
        add_metadata(df, walk_forward_type, fitness_function, train_size, repetition)
        generation_best_individuals_rows.append(df)


def add_metadata(df, walk_forward_type, fitness_function, train_size, repetition):
    df["walk_forward_type"] = walk_forward_type
    df["fitness_function"] = fitness_function
    df["train_size"] = train_size
    df["repetition"] = repetition


def create_global_best_so_far_df(generation_best_individuals_df):
    all_best_so_far_rows = []

    group_columns = [
        "walk_forward_type",
        "fitness_function",
        "train_size",
        "repetition",
    ]

    for group_values, group in generation_best_individuals_df.groupby(group_columns):
        best_so_far_df = create_best_so_far_df(group)

        walk_forward_type, fitness_function, train_size, repetition = group_values

        best_so_far_df["walk_forward_type"] = walk_forward_type
        best_so_far_df["fitness_function"] = fitness_function
        best_so_far_df["train_size"] = train_size
        best_so_far_df["repetition"] = repetition

        all_best_so_far_rows.append(best_so_far_df)

    if not all_best_so_far_rows:
        return pd.DataFrame()

    return pd.concat(all_best_so_far_rows, ignore_index=True)


def create_configuration_label(row):
    return (
        str(row["walk_forward_type"])
        + " | "
        + str(row["fitness_function"])
        + " | "
        + str(row["train_size"])
    )


def aggregate_metric_by_configuration_and_generation(
    df,
    generation_column,
    metric_column
):
    grouped = (
        df.groupby([
            "walk_forward_type",
            "fitness_function",
            "train_size",
            generation_column
        ])[metric_column]
        .mean()
        .reset_index()
    )

    grouped["configuration"] = grouped.apply(create_configuration_label, axis=1)

    return grouped


def plot_metric_all_configurations(
    df,
    generation_column,
    metric_column,
    title,
    ylabel,
    output_path
):
    grouped = aggregate_metric_by_configuration_and_generation(
        df,
        generation_column,
        metric_column
    )

    plt.figure(figsize=(12, 7))

    for configuration, config_group in grouped.groupby("configuration"):
        config_group = config_group.sort_values(generation_column)

        plt.plot(
            config_group[generation_column],
            config_group[metric_column],
            label=configuration
        )

    plt.title(title)
    plt.xlabel("Generation")
    plt.ylabel(ylabel)
    plt.legend(fontsize=8)
    plt.grid(True)

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()


def create_train_test_global_df(df, generation_column):
    group_columns = [
        "walk_forward_type",
        "fitness_function",
        "train_size",
        "repetition",
    ]

    all_rows = []

    for group_values, group in df.groupby(group_columns):
        train_test_df = create_train_test_fitness_df(
            group,
            generation_column=generation_column
        )

        walk_forward_type, fitness_function, train_size, repetition = group_values

        train_test_df["walk_forward_type"] = walk_forward_type
        train_test_df["fitness_function"] = fitness_function
        train_test_df["train_size"] = train_size
        train_test_df["repetition"] = repetition

        all_rows.append(train_test_df)

    if not all_rows:
        return pd.DataFrame()

    return pd.concat(all_rows, ignore_index=True)


def plot_train_vs_test_all_configurations(
    train_test_df,
    generation_column,
    title,
    output_path
):
    grouped = (
        train_test_df.groupby([
            "walk_forward_type",
            "fitness_function",
            "train_size",
            generation_column
        ])
        .agg(
            train_fitness=("train_fitness", "mean"),
            test_fitness=("test_fitness", "mean")
        )
        .reset_index()
    )

    grouped["configuration"] = grouped.apply(create_configuration_label, axis=1)

    plt.figure(figsize=(12, 7))

    for configuration, config_group in grouped.groupby("configuration"):
        config_group = config_group.sort_values(generation_column)

        plt.plot(
            config_group[generation_column],
            config_group["train_fitness"],
            label=f"{configuration} train"
        )

        plt.plot(
            config_group[generation_column],
            config_group["test_fitness"],
            linestyle="--",
            label=f"{configuration} test"
        )

    plt.title(title)
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.legend(fontsize=7)
    plt.grid(True)

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()


def create_learning_summary(all_generation_results_df, all_best_so_far_df):
    group_columns = [
        "walk_forward_type",
        "fitness_function",
        "train_size",
        "repetition",
        "window_id"
    ]

    summary_rows = []

    train_best_so_far_df = all_best_so_far_df[
        all_best_so_far_df["dataset_type"] == "train"
    ].copy()

    for group_values, group in all_generation_results_df.groupby(group_columns):
        group = group.sort_values("generation")

        first_row = group.iloc[0]
        last_row = group.iloc[-1]

        walk_forward_type, fitness_function, train_size, repetition, window_id = group_values

        best_group = train_best_so_far_df[
            (train_best_so_far_df["walk_forward_type"] == walk_forward_type)
            & (train_best_so_far_df["fitness_function"] == fitness_function)
            & (train_best_so_far_df["train_size"] == train_size)
            & (train_best_so_far_df["repetition"] == repetition)
            & (train_best_so_far_df["window_id"] == window_id)
        ].sort_values("analysis_generation")

        if best_group.empty:
            continue

        first_best = best_group.iloc[0]
        last_best = best_group.iloc[-1]

        row = {
            "walk_forward_type": walk_forward_type,
            "fitness_function": fitness_function,
            "train_size": train_size,
            "repetition": repetition,
            "window_id": window_id,

            "first_generation": first_row["generation"],
            "last_generation": last_row["generation"],

            "population_best_improvement": last_row["best_fitness"] - first_row["best_fitness"],
            "population_average_improvement": last_row["average_fitness"] - first_row["average_fitness"],
            "population_median_improvement": last_row["median_fitness"] - first_row["median_fitness"],

            "std_change": last_row["std_fitness"] - first_row["std_fitness"],
            "fitness_range_change": last_row["fitness_range"] - first_row["fitness_range"],

            "best_so_far_improvement": last_best["fitness"] - first_best["fitness"],
            "final_selected_generation": last_best["selected_generation"],
        }

        row["optimizer_learned"] = (
            row["population_average_improvement"] > 0
            and row["best_so_far_improvement"] > 0
        )

        summary_rows.append(row)

    return pd.DataFrame(summary_rows)


def create_overfitting_summary(train_test_df, generation_column):
    group_columns = [
        "walk_forward_type",
        "fitness_function",
        "train_size",
        "repetition",
        "window_id"
    ]

    summary_rows = []

    for group_values, group in train_test_df.groupby(group_columns):
        group = group.sort_values(generation_column)

        first_row = group.iloc[0]
        last_row = group.iloc[-1]

        train_improvement = last_row["train_fitness"] - first_row["train_fitness"]
        test_improvement = last_row["test_fitness"] - first_row["test_fitness"]
        gap_change = last_row["generalization_gap"] - first_row["generalization_gap"]

        walk_forward_type, fitness_function, train_size, repetition, window_id = group_values

        row = {
            "walk_forward_type": walk_forward_type,
            "fitness_function": fitness_function,
            "train_size": train_size,
            "repetition": repetition,
            "window_id": window_id,

            "first_generation": first_row[generation_column],
            "last_generation": last_row[generation_column],

            "train_improvement": train_improvement,
            "test_improvement": test_improvement,
            "gap_change": gap_change,

            "first_train_fitness": first_row["train_fitness"],
            "last_train_fitness": last_row["train_fitness"],

            "first_test_fitness": first_row["test_fitness"],
            "last_test_fitness": last_row["test_fitness"],

            "first_generalization_gap": first_row["generalization_gap"],
            "last_generalization_gap": last_row["generalization_gap"],
        }

        row["overfit_flag"] = (
            train_improvement > 0
            and test_improvement <= 0
            and gap_change > 0
        )

        summary_rows.append(row)

    return pd.DataFrame(summary_rows)


def create_configuration_summary(summary_df):
    summary = (
        summary_df.groupby([
            "walk_forward_type",
            "fitness_function",
            "train_size"
        ])
        .agg(
            mean_train_improvement=("train_improvement", "mean"),
            mean_test_improvement=("test_improvement", "mean"),
            mean_gap_change=("gap_change", "mean"),
            overfit_rate=("overfit_flag", "mean"),
            number_of_windows=("window_id", "count"),
        )
        .reset_index()
    )

    summary["configuration"] = summary.apply(create_configuration_label, axis=1)

    return summary


def run_global_generation_overfitting_analysis(
    results_folder_path,
    output_folder_path
):
    output_folder = Path(output_folder_path)
    output_folder.mkdir(parents=True, exist_ok=True)

    plots_folder = output_folder / "plots"
    plots_folder.mkdir(parents=True, exist_ok=True)

    all_generation_results_df, all_generation_best_individuals_df = (
        load_all_generation_files(results_folder_path)
    )

    if all_generation_results_df.empty:
        print("No generation_results.csv files found.")
        return None

    if all_generation_best_individuals_df.empty:
        print("No generation_best_individuals.csv files found.")
        return None

    all_best_so_far_df = create_global_best_so_far_df(
        all_generation_best_individuals_df
    )

    current_best_train_test_df = create_train_test_global_df(
        all_generation_best_individuals_df,
        generation_column="generation"
    )

    best_so_far_train_test_df = create_train_test_global_df(
        all_best_so_far_df,
        generation_column="analysis_generation"
    )

    learning_summary = create_learning_summary(
        all_generation_results_df,
        all_best_so_far_df
    )

    current_best_overfitting_summary = create_overfitting_summary(
        current_best_train_test_df,
        generation_column="generation"
    )

    best_so_far_overfitting_summary = create_overfitting_summary(
        best_so_far_train_test_df,
        generation_column="analysis_generation"
    )

    current_best_configuration_summary = create_configuration_summary(
        current_best_overfitting_summary
    )

    best_so_far_configuration_summary = create_configuration_summary(
        best_so_far_overfitting_summary
    )

    all_generation_results_df.to_csv(
        output_folder / "all_generation_results.csv",
        index=False
    )

    all_generation_best_individuals_df.to_csv(
        output_folder / "all_generation_best_individuals.csv",
        index=False
    )

    all_best_so_far_df.to_csv(
        output_folder / "all_best_so_far.csv",
        index=False
    )

    current_best_train_test_df.to_csv(
        output_folder / "current_best_train_test_fitness.csv",
        index=False
    )

    best_so_far_train_test_df.to_csv(
        output_folder / "best_so_far_train_test_fitness.csv",
        index=False
    )

    learning_summary.to_csv(
        output_folder / "generation_learning_summary.csv",
        index=False
    )

    current_best_overfitting_summary.to_csv(
        output_folder / "current_best_overfitting_summary.csv",
        index=False
    )

    best_so_far_overfitting_summary.to_csv(
        output_folder / "best_so_far_overfitting_summary.csv",
        index=False
    )

    current_best_configuration_summary.to_csv(
        output_folder / "current_best_overfitting_configuration_summary.csv",
        index=False
    )

    best_so_far_configuration_summary.to_csv(
        output_folder / "best_so_far_overfitting_configuration_summary.csv",
        index=False
    )

    # Generation learning plots
    plot_metric_all_configurations(
        all_generation_results_df,
        generation_column="generation",
        metric_column="average_fitness",
        title="Population average fitness by generation",
        ylabel="Average fitness",
        output_path=plots_folder / "population_average_fitness_all_configurations.png"
    )

    plot_metric_all_configurations(
        all_generation_results_df,
        generation_column="generation",
        metric_column="best_fitness",
        title="Population best fitness by generation",
        ylabel="Best fitness",
        output_path=plots_folder / "population_best_fitness_all_configurations.png"
    )

    plot_metric_all_configurations(
        all_generation_results_df,
        generation_column="generation",
        metric_column="std_fitness",
        title="Population fitness standard deviation by generation",
        ylabel="Fitness standard deviation",
        output_path=plots_folder / "population_std_fitness_all_configurations.png"
    )

    train_best_so_far_df = all_best_so_far_df[
        all_best_so_far_df["dataset_type"] == "train"
    ].copy()

    plot_metric_all_configurations(
        train_best_so_far_df,
        generation_column="analysis_generation",
        metric_column="fitness",
        title="Best-so-far train fitness by generation",
        ylabel="Best-so-far train fitness",
        output_path=plots_folder / "best_so_far_train_fitness_all_configurations.png"
    )

    plot_metric_all_configurations(
        train_best_so_far_df,
        generation_column="analysis_generation",
        metric_column="selected_generation",
        title="Selected generation by analysis generation",
        ylabel="Selected generation",
        output_path=plots_folder / "selected_generation_all_configurations.png"
    )

    # Overfitting plots
    plot_train_vs_test_all_configurations(
        current_best_train_test_df,
        generation_column="generation",
        title="Current best train vs test fitness by generation",
        output_path=plots_folder / "current_best_train_vs_test_all_configurations.png"
    )

    plot_metric_all_configurations(
        current_best_train_test_df,
        generation_column="generation",
        metric_column="generalization_gap",
        title="Current best generalization gap by generation",
        ylabel="Train fitness - test fitness",
        output_path=plots_folder / "current_best_gap_all_configurations.png"
    )

    plot_train_vs_test_all_configurations(
        best_so_far_train_test_df,
        generation_column="analysis_generation",
        title="Best-so-far train vs test fitness by generation",
        output_path=plots_folder / "best_so_far_train_vs_test_all_configurations.png"
    )

    plot_metric_all_configurations(
        best_so_far_train_test_df,
        generation_column="analysis_generation",
        metric_column="generalization_gap",
        title="Best-so-far generalization gap by generation",
        ylabel="Train fitness - test fitness",
        output_path=plots_folder / "best_so_far_gap_all_configurations.png"
    )

    return {
        "all_generation_results": all_generation_results_df,
        "all_generation_best_individuals": all_generation_best_individuals_df,
        "all_best_so_far": all_best_so_far_df,
        "current_best_train_test": current_best_train_test_df,
        "best_so_far_train_test": best_so_far_train_test_df,
        "learning_summary": learning_summary,
        "current_best_overfitting_summary": current_best_overfitting_summary,
        "best_so_far_overfitting_summary": best_so_far_overfitting_summary,
        "current_best_configuration_summary": current_best_configuration_summary,
        "best_so_far_configuration_summary": best_so_far_configuration_summary,
    }