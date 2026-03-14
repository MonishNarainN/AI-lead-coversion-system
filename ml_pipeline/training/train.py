import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

from services.preprocessing_service import PreprocessingService
from utils.column_mapper import ColumnMapper


def train_model(data_path, save_path):

    print("Loading dataset...")
    df = pd.read_csv(data_path)

    if "Converted" not in df.columns:
        raise ValueError("Target column 'Converted' not found in dataset")

    # Initialize production preprocessing tools
    mapper = ColumnMapper()
    preprocessor = PreprocessingService()

    # =========================
    # ALIGN COLUMNS
    # =========================
    print("Aligning columns...")
    aligned_df = mapper.align_columns(df)

    # =========================
    # PREPROCESS FEATURES
    # =========================
    print("Preprocessing data...")
    X = preprocessor.preprocess(aligned_df)

    # target
    y = df["Converted"]

    # =========================
    # TRAIN TEST SPLIT
    # =========================
    print("Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # =========================
    # DEFINE ENSEMBLE
    # =========================
    print("Building ensemble model...")

    clf1 = RandomForestClassifier(
        n_estimators=150,
        random_state=42,
        n_jobs=-1
    )

    clf2 = GradientBoostingClassifier(
        n_estimators=150,
        random_state=42
    )

    ensemble = VotingClassifier(
        estimators=[("rf", clf1), ("gb", clf2)],
        voting="soft"
    )

    # =========================
    # TRAIN MODEL
    # =========================
    print("Training model...")
    ensemble.fit(X_train, y_train)

    # =========================
    # EVALUATE
    # =========================
    print("\nModel Evaluation:\n")
    y_pred = ensemble.predict(X_test)
    print(classification_report(y_test, y_pred))

    # =========================
    # SAVE MODEL + FEATURES
    # =========================
    print("\nSaving model...")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # save model
    joblib.dump(ensemble, save_path)

    # save feature order
    feature_path = save_path.replace("ensemble_model.pkl", "features.pkl")
    joblib.dump(X.columns.tolist(), feature_path)

    print("Saved files:")
    print("Model ->", save_path)
    print("Features ->", feature_path)


# =========================
# RUN TRAINING
# =========================
if __name__ == "__main__":

    train_model(
        data_path="data/raw/leads_train.csv",
        save_path="backend/models/ensemble_model.pkl"
    )