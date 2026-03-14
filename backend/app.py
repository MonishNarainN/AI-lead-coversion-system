import os
import hashlib
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Import Middlewares
from middleware.logger import init_logger
from middleware.error_handler import init_error_handlers

# Import Services
from services.schema_service import detect_schema
from services.validation_service import validate_dataframe
from services.prediction_service import PredictionService
from services.preprocessing_service import PreprocessingService
from services.report_service import generate_csv_report, generate_excel_report, generate_analysis_report, generate_insights_report, generate_pdf_report
from services.explainability_service import compute_feature_importance, generate_business_recommendations
from services.audit_service import log_event

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB
CORS(app)

# Initialize Middlewares
init_logger(app)
init_error_handlers(app)

# Configuration — paths are anchored to this file's directory
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(_BASE_DIR, os.environ.get('UPLOAD_FOLDER', 'uploads'))
MODEL_PATH = os.path.join(_BASE_DIR, os.environ.get('MODEL_PATH', 'models/ensemble_model.pkl'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize ML Services
prediction_service = PredictionService(MODEL_PATH)
preprocessor = PreprocessingService()

# In-memory Result Cache (MD5 hash -> results)
# In production, use Redis or Disk Cache
result_cache = {}

def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "version": "2.0.0"})

@app.route('/metrics', methods=['GET'])
def metrics():
    return jsonify({
        "cached_predictions": len(result_cache),
        "model_version": "ensemble_v1",
        "status": "operational"
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    log_event("file_upload", "anonymous", {"filename": file.filename})
    
    # Trigger auto-schema detection on upload
    schema_report = detect_schema(file_path)
    
    return jsonify({
        "message": "File uploaded successfully",
        "filename": file.filename,
        "schema": schema_report
    })

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({"error": "Filename required"}), 400
        
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Check Cache
    file_hash = get_file_hash(file_path)
    if file_hash in result_cache:
        log_event("prediction_request", "anonymous", {"filename": filename, "cache": "hit"})
        return jsonify({**result_cache[file_hash], "cached": True})

    # Processing
    try:
        import pandas as pd
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # 1. Validate
        validation_report = validate_dataframe(df)
        
        # 2. Preprocess
        processed_df = preprocessor.preprocess(df)
        
        # 3. Predict
        predictions_df = prediction_service.predict(processed_df)
        
        # 4. Explainability & Insights
        # Increase sample to 500 for more stable permutation importance
        feature_importance = compute_feature_importance(processed_df.head(500), prediction_service.model)
        
        # Summary stats
        total_leads = len(predictions_df)
        conversions = int(predictions_df['Converted_Prediction'].sum())
        avg_prob = float(predictions_df['Conversion_Probability'].mean())
        hot_count = int((predictions_df['Conversion_Probability'] >= 0.80).sum())
        
        summary = {
            "total_leads": total_leads,
            "hot_leads": hot_count,
            "expected_conversions": conversions,
            "avg_probability": avg_prob,
            "conversion_rate": conversions / max(total_leads, 1)
        }
        
        # Distribution
        dist = predictions_df['Decision'].value_counts().to_dict()
        normalized_dist = {
            "Hot Lead": int(dist.get("Hot Lead: Instant follow-up recommended", 0)),
            "Warm Lead": int(dist.get("Warm Lead: Nurture with personalized content", 0)),
            "Cold Lead": int(dist.get("Cold Lead: Low priority, automated engagement", 0))
        }
        
        # Precision / Recall / F1
        # Since we have no ground truth labels, we treat the top-30% percentile
        # ("Converted_Prediction") as the positive class and compute self-consistency
        # metrics between the probability threshold and the percentile-based label.
        from sklearn.metrics import precision_score, recall_score, f1_score
        try:
            y_prob = predictions_df['Conversion_Probability'].values
            y_pred = predictions_df['Converted_Prediction'].values
            # Use 0.5 as the probability threshold to derive a "soft" ground truth
            y_soft = (y_prob >= 0.50).astype(int)
            precision = float(precision_score(y_soft, y_pred, zero_division=0))
            recall    = float(recall_score(y_soft, y_pred, zero_division=0))
            f1        = float(f1_score(y_soft, y_pred, zero_division=0))
            support   = int(y_soft.sum())
            note = "Computed against a 0.50 probability threshold (no ground truth labels available)"
        except Exception:
            precision, recall, f1, support = 0.0, 0.0, 0.0, 0
            note = "Metrics unavailable"
        
        metrics = {
            "precision": round(precision, 4),
            "recall":    round(recall, 4),
            "f1":        round(f1, 4),
            "support":   support,
            "note":      note
        }
        
        # Recommendations
        recommendations = generate_business_recommendations(summary, normalized_dist, feature_importance)
        
        # Detailed data: only Hot Leads (≥ 80% confidence), top 100 sorted by probability
        hot_leads_df = (
            predictions_df[predictions_df['Conversion_Probability'] >= 0.80]
            .sort_values('Conversion_Probability', ascending=False)
            .head(100)
        )
        result = {
            "summary": summary,
            "metrics": metrics,
            "distribution": normalized_dist,
            "feature_importance": feature_importance,
            "recommendations": recommendations,
            "data": hot_leads_df.to_dict(orient='records'),
            "cached": False
        }
        
        # Save to cache
        result_cache[file_hash] = result
        log_event("prediction_request", "anonymous", {"filename": filename, "cache": "miss", "leads": total_leads})
        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/reports/download', methods=['POST'])
def download_report():
    import pandas as pd
    from io import BytesIO

    data = request.get_json()
    filename = data.get('filename')
    format_type = data.get('format', 'csv')
    
    if not filename:
        return jsonify({"error": "Filename required"}), 400
        
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        # Load original file (keep all columns for the report)
        raw_df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
        
        # Run prediction pipeline
        processed_df = preprocessor.preprocess(raw_df)
        predictions_df = prediction_service.predict(processed_df)
        
        # Merge original columns + prediction columns for a rich report
        pred_cols = ['Conversion_Probability', 'Converted_Prediction', 'Decision']
        
        # Drop these columns from raw_df if they already exist to avoid duplicates
        raw_df_clean = raw_df.drop(columns=[c for c in pred_cols if c in raw_df.columns])
        
        raw_df_reset = raw_df_clean.reset_index(drop=True)
        preds_reset  = predictions_df[pred_cols].reset_index(drop=True)
        report_df = pd.concat([raw_df_reset, preds_reset], axis=1)

        # Distribution (Needed for analysis report)
        dist = predictions_df['Decision'].value_counts().to_dict()
        normalized_dist = {
            "Hot Lead": int(dist.get("Hot Lead: Instant follow-up recommended", 0)),
            "Warm Lead": int(dist.get("Warm Lead: Nurture with personalized content", 0)),
            "Cold Lead": int(dist.get("Cold Lead: Low priority, automated engagement", 0))
        }

        # Feature Importance (Needed for insights report)
        # Increase sample to 500 for more stable permutation importance
        feature_importance = compute_feature_importance(processed_df.head(500), prediction_service.model)

        # Build summary
        total = len(predictions_df)
        conversions = int(predictions_df['Converted_Prediction'].sum())
        summary = {
            "total_leads":           total,
            "hot_leads":             int((predictions_df['Conversion_Probability'] >= 0.80).sum()),
            "expected_conversions":  conversions,
            "avg_probability":       float(predictions_df['Conversion_Probability'].mean()),
            "conversion_rate":       conversions / max(total, 1)
        }
        
        # Re-compute metrics
        from sklearn.metrics import precision_score, recall_score, f1_score
        y_prob = predictions_df['Conversion_Probability'].values
        y_pred = predictions_df['Converted_Prediction'].values
        y_soft = (y_prob >= 0.50).astype(int)
        metrics = {
            "precision": round(float(precision_score(y_soft, y_pred, zero_division=0)), 4),
            "recall":    round(float(recall_score(y_soft, y_pred, zero_division=0)), 4),
            "f1":        round(float(f1_score(y_soft, y_pred, zero_division=0)), 4),
            "support":   int(y_soft.sum()),
            "note":      "Computed against a 0.50 probability threshold"
        }
        
        if format_type == 'excel':
            report_bytes = generate_excel_report(report_df, summary, metrics)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            out_filename = f"lead_report_{filename.rsplit('.', 1)[0]}.xlsx"
        elif format_type == 'analysis':
            report_bytes = generate_analysis_report(summary, metrics, normalized_dist)
            mimetype = 'text/csv'
            out_filename = f"lead_analysis_{filename.rsplit('.', 1)[0]}.csv"
        elif format_type == 'insights':
            # Get recommendations for the report
            recommendations = generate_business_recommendations(summary, normalized_dist, feature_importance)
            report_bytes = generate_insights_report(recommendations, feature_importance)
            mimetype = 'text/plain'
            out_filename = f"lead_insights_{filename.rsplit('.', 1)[0]}.txt"
        elif format_type == 'pdf':
            try:
                print("DEBUG: Starting PDF generation path...")
                recommendations = generate_business_recommendations(summary, normalized_dist, feature_importance)
                print(f"DEBUG: Recommendations generated ({len(recommendations)})")
                
                print("DEBUG: Calling generate_pdf_report...")
                report_bytes = generate_pdf_report(summary, metrics, normalized_dist, recommendations, feature_importance)
                print(f"DEBUG: generate_pdf_report SUCCESS ({len(report_bytes)} bytes)")
                
                mimetype = 'application/pdf'
                out_filename = f"lead_analysis_{filename.rsplit('.', 1)[0]}.pdf"
            except Exception as pdf_err:
                print(f"DEBUG: PDF generation CATCH: {pdf_err}")
                import traceback
                traceback.print_exc()
                return jsonify({"error": f"PDF generation failed: {str(pdf_err)}"}), 500
        else: # predictions / default csv
            report_bytes = generate_csv_report(report_df)
            mimetype = 'text/csv'
            out_filename = f"lead_predictions_{filename.rsplit('.', 1)[0]}.csv"
            
        return send_file(
            BytesIO(report_bytes),
            mimetype=mimetype,
            as_attachment=True,
            download_name=out_filename
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')
