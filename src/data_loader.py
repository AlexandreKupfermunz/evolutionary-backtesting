import pandas as pd

def load_data(file_path, nrows=None):

    df = pd.read_csv(file_path, nrows=nrows)
    df.columns = df.columns.str.strip()

    # This replaces all 0s by 1s
    df["AskVolume"] = df["AskVolume"].replace(0,1)
    df["BidVolume"] = df["BidVolume"].replace(0,1)

    return df