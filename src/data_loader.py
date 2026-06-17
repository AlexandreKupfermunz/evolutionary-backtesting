import pandas as pd

def load_data(file_path, nrows=None):
    df = pd.read_csv(file_path, nrows=nrows)
    df.columns = df.columns.str.strip()
    return df