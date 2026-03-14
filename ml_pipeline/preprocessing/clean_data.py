import pandas as pd
import numpy as np

def clean_data(df, missing_threshold=0.7):
    """
    Cleans dataset for ML pipeline.

    Steps:
    - Validates input
    - Standardizes column names
    - Fixes categorical inconsistencies
    - Drops columns with too many missing values
    """

    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Fix dataset-specific issues
    if 'country' in df.columns:
        df['country'] = df['country'].astype(str).str.title()

    # Drop columns with too many missing values
    original_cols = df.shape[1]
    threshold = len(df) * missing_threshold
    df = df.dropna(thresh=threshold, axis=1)
    dropped_cols = original_cols - df.shape[1]

    print(f"[INFO] Dropped {dropped_cols} columns due to missing values")

    return df


if __name__ == "__main__":
    print("Data cleaning module loaded successfully.")