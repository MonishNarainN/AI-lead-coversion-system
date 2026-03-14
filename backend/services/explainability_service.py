import pandas as pd
import numpy as np


def compute_feature_importance(X: pd.DataFrame, model) -> list:
    """
    Compute feature importance using Permutation Importance.
    This is model-agnostic and works with VotingClassifier, unlike SHAP TreeExplainer.
    It calculates how much the performance drops when a feature is shuffled.
    """
    try:
        from sklearn.inspection import permutation_importance
        
        # We need a 'y' for permutation importance. Since we don't have true labels
        # during prediction, we use the model's own predictions as a proxy ground truth.
        # This effectively measures which features the model is actually using for its decisions.
        y_proxy = model.predict(X)
        
        # Calculate permutation importance (5 repeats for stability)
        r = permutation_importance(model, X, y_proxy, n_repeats=5, random_state=42)
        
        importance = sorted(
            [{"feature": col, "importance": round(float(v), 4)} for col, v in zip(X.columns, r.importances_mean)],
            key=lambda x: x["importance"],
            reverse=True
        )
        # Ensure we don't have negative importance (artifact of low sample/noise)
        for item in importance:
            if item['importance'] < 0:
                item['importance'] = 0.0
                
        return importance[:10]

    except Exception as e:
        print(f"Permutation importance failed: {e}")
        # Fallback 1: use built-in feature_importances_ if available (e.g. if single tree inside)
        try:
            importances = getattr(model, 'feature_importances_', None)
            if importances is not None:
                importance = sorted(
                    [{"feature": col, "importance": round(float(v), 4)} for col, v in zip(X.columns, importances)],
                    key=lambda x: x["importance"],
                    reverse=True
                )
                return importance[:10]
        except Exception:
            pass

    # Last resort: equal weights (only if everything else fails)
    return [{"feature": col, "importance": round(1.0 / len(X.columns), 4)} for col in X.columns[:10]]


def generate_business_recommendations(summary: dict, distribution: dict, feature_importance: list = None) -> list:
    """
    Generate actionable business recommendations from prediction summary, distribution, and feature importance.
    """
    recs = []
    total = summary.get("total_leads", 1)
    hot = distribution.get("Hot Lead", 0)
    warm = distribution.get("Warm Lead", 0)
    cold = distribution.get("Cold Lead", 0)
    conversion_rate = summary.get("conversion_rate", 0)

    hot_pct = round(hot / total * 100, 1) if total else 0
    warm_pct = round(warm / total * 100, 1) if total else 0
    cold_pct = round(cold / total * 100, 1) if total else 0

    # 1. Distribution-based Recommendations (Dynamic thresholds)
    if hot_pct > 25:
        recs.append({
            "type": "success",
            "title": "High-Value Lead Density",
            "message": f"Exceptional lead quality: {hot_pct}% of the dataset are Hot leads. Prioritize immediate 1-on-1 calls for this segment."
        })
    elif hot_pct < 5:
        recs.append({
            "type": "warning",
            "title": "Top-Funnel Weakness",
            "message": f"Only {hot_pct}% Hot leads detected. Review the source of these leads and consider high-intent targeting."
        })

    if warm_pct > 40:
        recs.append({
             "type": "info",
             "title": "Middle-Funnel Opportunity",
             "message": f"Large warm segment ({warm_pct}%). Deploy automated email drip campaigns with case studies to push them to Hot status."
        })

    # 2. Feature-based Insights (Truly Dynamic)
    if feature_importance and len(feature_importance) > 0:
        top_feat = feature_importance[0]
        feat_name = top_feat['feature'].replace('_', ' ').title()
        
        recs.append({
            "type": "info",
            "title": f"Key Driver: {feat_name}",
            "message": f"'{feat_name}' is the strongest predictor of conversion in this dataset. Ensure your sales team captures accurate data for this field."
        })

        if any(f['feature'] == 'timespentonwebsite' for f in feature_importance[:3]):
            recs.append({
                "type": "success",
                "title": "Behavioral Signal Strength",
                "message": "Time spent on website is a top driver. Focus on improving landing page engagement to boost potential conversions."
            })
            
        if any(f['feature'] == 'totalvisits' for f in feature_importance[:3]):
             recs.append({
                "type": "info",
                "title": "Traffic Volume Insight",
                "message": "High visit counts are strongly correlating with quality. Your repeat visitors are your best prospects."
            })

    # 3. Data Quality Insights (Dynamic based on nulls or unknowns)
    # Note: In a real scenario, we'd pass the original DF too.
    # For now, we can infer some quality issues from the distribution of 'Cold Leads'
    if cold_pct > 60:
         recs.append({
            "type": "warning",
            "title": "Data Quality Alert",
            "message": "Over 60% of leads are classified as Cold. Check if key fields like 'Lead Source' or 'Last Activity' have high missing values or 'Unknown' categories."
        })

    # 3. Performance Insights
    if conversion_rate > 0.4:
        recs.append({
            "type": "success",
            "title": "High Conversion Performance",
            "message": f"Predicted average conversion rate is {conversion_rate:.1%}. This dataset shows strong alignment with your historical success."
        })
    elif conversion_rate < 0.15:
         recs.append({
            "type": "warning",
            "title": "Low Overall Conversion",
            "message": f"Dataset average conversion is low ({conversion_rate:.1%}). Focus strictly on the Hot leads segment (≥80%) to maximize efficiency."
        })

    if not recs:
        recs.append({
            "type": "info",
            "title": "Stable Pipeline",
            "message": "The lead distribution is typical for your average campaign. Maintain current outreach velocity."
        })

    return recs
