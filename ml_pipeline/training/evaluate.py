import os
import json
import joblib
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report
)

from services.preprocessing_service import PreprocessingService
from utils.column_mapper import ColumnMapper


def evaluate_model(model_path, test_data_path, output_path="ml_pipeline/evaluation_results.json"):
    # ---------- Load Model ----------
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = joblib.load(model_path)

    # ---------- Load Data ----------
    if not os.path.exists(test_data_path):
        raise FileNotFoundError(f"Test dataset not found: {test_data_path}")

    df = pd.read_csv(test_data_path)

    if "Converted" not in df.columns:
        raise ValueError("Target column 'Converted' missing in test dataset.")

    # ---------- Production-Level Preprocessing ----------
    mapper = ColumnMapper()
    preprocessor = PreprocessingService()

    aligned_df = mapper.align_columns(df)

    X_test = preprocessor.preprocess(aligned_df)
    y_test = df["Converted"]

    # ---------- Predict ----------
    y_pred = model.predict(X_test)

    # ---------- Metrics ----------
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1_score": float(f1_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, output_dict=True)
    }

    # ---------- Save Results ----------
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print("\nEvaluation Complete")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    # Example:
    # evaluate_model(
    #     model_path="backend/models/ensemble_model.pkl",
    #     test_data_path="data/raw/leads_test.csv"
    # )
    pass