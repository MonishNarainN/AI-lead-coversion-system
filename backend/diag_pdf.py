import pandas as pd
import numpy as np
import joblib
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from services.prediction_service import PredictionService
from services.preprocessing_service import PreprocessingService
from services.report_service import generate_pdf_report
from services.explainability_service import generate_business_recommendations, compute_feature_importance

def diag():
    print("Starting diagnostics...")
    MODEL_PATH = 'models/ensemble_model.pkl'
    FILENAME = 'lead_predictions.csv'
    UPLOAD_FOLDER = 'uploads'
    
    file_path = os.path.join(UPLOAD_FOLDER, FILENAME)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    
    print("Initializing services...")
    prediction_service = PredictionService(MODEL_PATH)
    preprocessor = PreprocessingService()
    
    print("Preprocessing...")
    processed_df = preprocessor.preprocess(df)
    
    print("Predicting...")
    predictions_df = prediction_service.predict(processed_df)
    
    print("Computing metrics...")
    total = len(predictions_df)
    conversions = int(predictions_df['Converted_Prediction'].sum())
    summary = {
        "total_leads": total,
        "hot_leads": int((predictions_df['Conversion_Probability'] >= 0.80).sum()),
        "expected_conversions": conversions,
        "avg_probability": float(predictions_df['Conversion_Probability'].mean()),
        "conversion_rate": conversions / max(total, 1)
    }
    
    dist = predictions_df['Decision'].value_counts().to_dict()
    normalized_dist = {
        "Hot Lead": int(dist.get("Hot Lead: Instant follow-up recommended", 0)),
        "Warm Lead": int(dist.get("Warm Lead: Nurture with personalized content", 0)),
        "Cold Lead": int(dist.get("Cold Lead: Low priority, automated engagement", 0))
    }
    
    metrics = {"precision": 0.5, "recall": 0.5, "f1": 0.5, "support": 100, "note": "diag"}
    
    print("Computing feature importance (500 rows)...")
    try:
        feature_importance = compute_feature_importance(processed_df.head(500), prediction_service.model)
        print(f"Feature importance computed: {len(feature_importance)} features")
    except Exception as e:
        print(f"Importance calculation failed: {e}")
        feature_importance = []

    print("Generating recommendations...")
    recommendations = generate_business_recommendations(summary, normalized_dist, feature_importance)
    
    print("Generating PDF report...")
    try:
        report_bytes = generate_pdf_report(summary, metrics, normalized_dist, recommendations, feature_importance)
        print(f"SUCCESS: Generated {len(report_bytes)} bytes")
        with open('diag_report.pdf', 'wb') as f:
            f.write(report_bytes)
        print("Written to diag_report.pdf")
    except Exception as e:
        print(f"PDF GENERATION FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diag()
