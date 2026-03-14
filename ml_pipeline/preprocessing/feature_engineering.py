import pandas as pd

def engineer_features(df):
    """
    Generates new features for model training.

    Steps:
    - Validate input
    - Create engagement score
    - Generate time-based features (if timestamp exists)
    """

    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    # ---- Engagement Score ----
    if 'total_visits' in df.columns and 'pageviews_per_visit' in df.columns:
        df['engagement_score'] = (
            pd.to_numeric(df['total_visits'], errors='coerce') *
            pd.to_numeric(df['pageviews_per_visit'], errors='coerce')
        )

    # ---- Time Features ----
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        df['is_weekend'] = df['created_at'].dt.weekday >= 5
        df['hour'] = df['created_at'].dt.hour

    return df


if __name__ == "__main__":
    print("Feature engineering module ready.")