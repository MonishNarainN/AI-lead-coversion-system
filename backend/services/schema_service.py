import pandas as pd
import numpy as np


def detect_schema(file_path: str) -> dict:
    """
    Auto-detect schema from a CSV/Excel file.
    Returns a structured report with column names, types, null %, unique counts,
    and a data quality score.
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, nrows=1000)  # Sample first 1000 rows for speed
        else:
            df = pd.read_excel(file_path, nrows=1000)
    except Exception as e:
        return {"error": f"Could not read file: {str(e)}"}

    total_rows = len(df)
    columns = []
    quality_deductions = 0

    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_pct = round(null_count / max(total_rows, 1) * 100, 1)
        unique_count = int(df[col].nunique())
        dtype = str(df[col].dtype)

        # Infer semantic type
        if pd.api.types.is_numeric_dtype(df[col]):
            semantic = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            semantic = "datetime"
        elif unique_count / max(total_rows, 1) < 0.05:
            semantic = "categorical"
        else:
            semantic = "text"

        # Quality penalty
        if null_pct > 80:
            quality_deductions += 10
        elif null_pct > 30:
            quality_deductions += 3

        columns.append({
            "name": col,
            "dtype": dtype,
            "semantic_type": semantic,
            "null_count": null_count,
            "null_pct": null_pct,
            "unique_count": unique_count,
            "sample_values": [str(v) for v in df[col].dropna().head(3).tolist()]
        })

    quality_score = max(0, 100 - quality_deductions)

    return {
        "total_rows_sampled": total_rows,
        "total_columns": len(df.columns),
        "quality_score": quality_score,
        "columns": columns
    }
