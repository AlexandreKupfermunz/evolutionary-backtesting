def calculate_summary_statistics(df, metric):

    metric_df = df[metric]

    mean = metric_df.mean()
    median = metric_df.median()
    std = metric_df.std()
    minimum = metric_df.min()
    maximum = metric_df.max()

    dictionary = {
        "mean": mean,
        "median": median,
        "std": std,
        "minimum": minimum,
        "maximum": maximum
    }

    return dictionary

def summarize_by_group(df, metric, group_by):

    groupped_df = df.groupby(group_by)

    results = groupped_df.agg({
        metric: ["mean", "median", "std", "min", "max"]

    })

    return results

