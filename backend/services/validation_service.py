import pandas as pd
import numpy as np


def validate_dataframe(df: pd.DataFrame) -> dict:
    """
    Perform row-level and column-level data validation.
    Returns a structured validation report with a quality score and flagged rows.
    """
    issues = []
    flagged_rows = set()
    total_rows = len(df)
    
    col_reports = {}
    for col in df.columns:
        col_issues = []
        null_count = int(df[col].isnull().sum())
        null_pct = round(null_count / max(total_rows, 1) * 100, 1)

        if null_pct > 50:
            col_issues.append(f"High missing rate ({null_pct}%)")
            issues.append(f"Column '{col}': {null_pct}% missing values")

        if pd.api.types.is_numeric_dtype(df[col]):
            # Outlier detection (IQR method)
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outlier_mask = (df[col] < q1 - 3 * iqr) | (df[col] > q3 + 3 * iqr)
            outlier_rows = df.index[outlier_mask].tolist()
            if outlier_rows:
                col_issues.append(f"{len(outlier_rows)} extreme outliers detected")
                flagged_rows.update(outlier_rows[:20])  # Cap at 20

        col_reports[col] = {
            "null_pct": null_pct,
            "issues": col_issues
        }

    # Duplicate rows
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        issues.append(f"{dup_count} duplicate rows detected")

    # Quality score
    score_deductions = min(50, len(issues) * 5)
    score_deductions += min(30, (dup_count / max(total_rows, 1)) * 100)
    quality_score = max(0, round(100 - score_deductions))

    return {
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "duplicate_rows": dup_count,
        "quality_score": quality_score,
        "issues": issues,
        "flagged_row_count": len(flagged_rows),
        "column_reports": col_reports
    }
