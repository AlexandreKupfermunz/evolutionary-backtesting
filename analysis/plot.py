import matplotlib.pyplot as plt
from pathlib import Path

def plot_ga_convergence(df, metric):

    plt.figure(figsize=(10, 6))

    title = f"{metric} convergence"

    add_line(df, "generation", metric, label = metric)

    save_plot(df, title, "convergence")

def plot_train_vs_test(train_df, test_df, metric):

    title = f"{metric} evolution train vs test"

    add_line(train_df, "generation", metric, label = "Train")
    add_line(test_df, "generation", metric, label = "Test")
             
    save_plot(train_df, title, "overfitting")

def plot_metric_per_window(df, metric):

    plt.figure(figsize=(10, 6))

    title = f"{metric} per window"

    add_line(df, "window", metric, label=metric)

    save_plot(df, title, "window_metrics")

def plot_arameter_evolution(df, parameter):

    plt.figure(figsize=(10,6))

    title=f"{parameter} evolution"

    add_line(df, "generation", parameter, label=parameter)

    save_plot(df, title, "parameters")

def add_line(df, x_column, y_column, label):

    if df.empty:
        return

    x_axis = df[x_column]
    y_axis = df[y_column]

    plt.plot(x_axis, y_axis, label = label )

    plt.xlabel(x_column)
    plt.ylabel(y_column)

def save_plot(df, title, output_folder):

    plt.title(title)

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    walk_forward_type, fitness_function, train_size_name, repetition, csv_type = get_metadata(df)

    if train_size_name == None:
        train_size_name = ""

    file_name = f"{replace_invalid_car(title)}_{walk_forward_type}_{fitness_function}_{train_size_name}_{repetition}_{csv_type}"

    plot_path = get_plot_path(file_name, output_folder)

    plt.savefig(plot_path, format = "png")

    plt.close()

def get_plot_path(file_name, output_folder): 

    path = Path("analysis")

    output_path = path / "output"

    graphs_path = output_path / output_folder

    graphs_path.mkdir(parents = True, exist_ok = True)
    
    file_name = replace_invalid_car(file_name)

    plot_path = graphs_path / f"{file_name}.png"

    return plot_path

def replace_invalid_car(file_name):

    file_name = file_name.replace(" ", "_")
    file_name = file_name.replace("-", "_")
    file_name = file_name.replace(".", "_")
    file_name = file_name.replace(":", "_")
    
    return file_name

def get_metadata(df):

    walk_forward_type = df["walk_forward_type"].iloc[0]
    fitness_function = df["fitness_function"].iloc[0]
    train_size_name = df["train_size_name"].iloc[0]
    repetition = df["repetition"].iloc[0]
    csv_type = df["csv_type"].iloc[0]

    return walk_forward_type, fitness_function, train_size_name, repetition, csv_type