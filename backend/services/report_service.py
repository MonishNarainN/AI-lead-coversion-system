import pandas as pd
import io


def generate_csv_report(output_df: pd.DataFrame) -> bytes:
    """Generate a CSV report from prediction results."""
    buffer = io.BytesIO()
    # Ensure all object columns are string-safe
    df = _sanitize_df(output_df)
    df.to_csv(buffer, index=False, encoding='utf-8')
    buffer.seek(0)
    return buffer.getvalue()


def generate_excel_report(output_df: pd.DataFrame, summary: dict, metrics: dict = None) -> bytes:
    """
    Generate an Excel report with three sheets:
      - Predictions: full lead table with scores
      - Summary:     aggregate stats
      - ModelMetrics: Precision, Recall, F1, etc. (if provided)
    """
    buffer = io.BytesIO()
    df = _sanitize_df(output_df)

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Sheet 1: Full predictions
        df.to_excel(writer, index=False, sheet_name='Predictions')

        # Sheet 2: Summary
        summary_rows = [
            {"Metric": "Total Leads",                "Value": summary.get("total_leads", 0)},
            {"Metric": "Hot Leads (≥80%)",           "Value": summary.get("hot_leads", 0)},
            {"Metric": "Expected Conversions",        "Value": summary.get("expected_conversions", 0)},
            {"Metric": "Avg. Conversion Probability", "Value": f"{summary.get('avg_probability', 0):.2%}"},
            {"Metric": "Conversion Rate",             "Value": f"{summary.get('conversion_rate', 0):.2%}"},
        ]
        pd.DataFrame(summary_rows).to_excel(writer, index=False, sheet_name='Summary')

        # Sheet 3: Model Metrics (if available)
        if metrics:
            metrics_rows = [
                {"Metric": "Precision",  "Value": f"{metrics.get('precision', 0):.4f}"},
                {"Metric": "Recall",     "Value": f"{metrics.get('recall', 0):.4f}"},
                {"Metric": "F1-Score",   "Value": f"{metrics.get('f1', 0):.4f}"},
                {"Metric": "Support (positive class)", "Value": metrics.get('support', 'N/A')},
                {"Metric": "Note",       "Value": metrics.get('note', '')},
            ]
            pd.DataFrame(metrics_rows).to_excel(writer, index=False, sheet_name='ModelMetrics')

    buffer.seek(0)
    return buffer.getvalue()


def generate_analysis_report(summary: dict, metrics: dict, distribution: dict) -> bytes:
    """Generate a CSV report for the statistical analysis."""
    data = []
    # Add summary
    for k, v in summary.items():
        data.append({"Category": "Summary", "Metric": k.replace('_',' ').title(), "Value": v})
    # Add metrics
    for k, v in metrics.items():
        data.append({"Category": "Accuracy", "Metric": k.title(), "Value": v})
    # Add distribution
    for k, v in distribution.items():
        data.append({"Category": "Distribution", "Metric": k, "Value": v})
    
    buffer = io.BytesIO()
    pd.DataFrame(data).to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()


def generate_insights_report(recommendations: list, feature_importance: list) -> bytes:
    """Generate a text report for AI insights."""
    lines = ["--- AI BUSINESS INSIGHTS REPORT ---\n"]
    
    lines.append("\n[STRATEGIC RECOMMENDATIONS]")
    for rec in recommendations:
        lines.append(f"- {rec['title'].upper()}: {rec['message']}")
    
    lines.append("\n[PREDICTIVE DRIVERS (Top 10 Features)]")
    if feature_importance:
        for f in feature_importance:
            lines.append(f"- {f['feature']}: {f['importance']:.4f}")
    else:
        lines.append("- No feature importance data available.")
        
    buffer = io.BytesIO()
    buffer.write("\n".join(lines).encode('utf-8'))
    buffer.seek(0)
    return buffer.getvalue()


def generate_pdf_report(summary: dict, metrics: dict, distribution: dict, recommendations: list, feature_importance: list) -> bytes:
    """
    Generate a professional PDF analytics report using fpdf2.
    """
    from fpdf import FPDF
    import datetime

    class PDF(FPDF):
        def header(self):
            # Banner color
            self.set_fill_color(99, 102, 241) # Primary indigo
            self.rect(0, 0, 210, 40, 'F')
            
            self.set_font('helvetica', 'B', 24)
            self.set_text_color(255, 255, 255)
            self.cell(0, 20, 'AI Lead Conversion Intelligence', ln=True, align='L')
            
            self.set_font('helvetica', 'I', 10)
            date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cell(0, 5, f'Generated at: {date_str}', ln=True, align='L')
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f'Page {self.page_no()} | AI Lead Intelligence Platform', align='C')

    def _s(text):
        """Sanitize string for fpdf2 default latin-1 fonts."""
        if not isinstance(text, str):
            text = str(text)
        return text.encode('latin-1', 'replace').decode('latin-1')

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # 1. Dashboard Summary Section
    pdf.set_font('helvetica', 'B', 16)
    pdf.set_text_color(31, 41, 55) # Dark gray
    pdf.cell(0, 10, 'I. Executive Summary', ln=True)
    pdf.ln(2)
    
    # Simple grid for stats
    pdf.set_font('helvetica', '', 12)
    stats = [
        ("Total Leads Analyzed", f"{summary.get('total_leads', 0)}"),
        ("Hot Leads Identified", f"{summary.get('hot_leads', 0)}"),
        ("Expected Conversions", f"{summary.get('expected_conversions', 0)}"),
        ("Avg. Conversion Prob", f"{summary.get('avg_probability', 0):.1%}"),
        ("Accuracy (F1 Score)", f"{metrics.get('f1', 0):.4f}")
    ]
    
    for label, val in stats:
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(50, 8, _s(f"{label}:"), border=0)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 8, _s(val), ln=True)
    
    pdf.ln(10)
    
    # 2. Lead Distribution Section
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, 'II. Lead Quality Distribution', ln=True)
    pdf.ln(2)
    
    # Table header
    pdf.set_fill_color(243, 244, 246)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(60, 10, 'Category', border=1, fill=True)
    pdf.cell(60, 10, 'Count', border=1, fill=True)
    pdf.cell(60, 10, 'Percentage', border=1, ln=True, fill=True)
    
    total = summary.get('total_leads', 1)
    pdf.set_font('helvetica', '', 10)
    for cat, count in distribution.items():
        pct = (count / total) * 100 if total else 0
        pdf.cell(60, 10, _s(cat), border=1)
        pdf.cell(60, 10, str(count), border=1)
        pdf.cell(60, 10, _s(f"{pct:.1f}%"), border=1, ln=True)
    
    pdf.ln(10)
    
    # 3. AI Insights Section
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, 'III. Strategic AI Insights', ln=True)
    pdf.ln(2)
    
    for rec in recommendations:
        # Mini Card for Recommendation
        pdf.set_fill_color(249, 250, 251)
        pdf.set_font('helvetica', 'B', 11)
        # title
        title = f"[{rec['type'].upper()}] {rec['title']}"
        pdf.cell(0, 8, _s(title), ln=True, fill=True)
        # message
        pdf.set_font('helvetica', '', 10)
        pdf.multi_cell(0, 6, _s(rec['message']), border='B')
        pdf.ln(4)
        
    pdf.ln(5)
    
    # 4. Feature Importance Section
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, 'IV. Predictive Drivers (Top Features)', ln=True)
    pdf.ln(2)
    
    pdf.set_font('helvetica', 'I', 9)
    pdf.multi_cell(0, 5, "These features show the strongest correlation with conversion outcomes for this specific dataset.")
    pdf.ln(4)
    
    if feature_importance:
        importances = [f['importance'] for f in feature_importance]
        max_imp = max(importances) if importances and max(importances) > 0 else 1
        
        for f in feature_importance[:5]:
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(60, 8, _s(f['feature']), ln=0)
            
            # Draw a progress bar
            importance_val = max(0, f['importance'])
            bar_width = (importance_val / max_imp) * 100
            # Ensure bar_width isn't absurdly small for visibility or 0
            bar_width = max(1, bar_width) if importance_val > 0 else 0
            
            pdf.set_fill_color(129, 140, 248) # Indigo 400
            pdf.cell(bar_width, 6, '', border=0, fill=True)
            pdf.set_font('helvetica', '', 9)
            pdf.cell(10, 6, f" {importance_val:.4f}", ln=True)
            pdf.ln(2)
    else:
        pdf.cell(0, 10, 'No feature importance data available.', ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


def _sanitize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Convert any non-serialisable types to strings so openpyxl doesn't crash."""
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str)
        # Convert numpy int/float types that openpyxl struggles with
        try:
            import numpy as np
            if df[col].dtype in [np.int64, np.int32]:
                df[col] = df[col].astype(int)
            elif df[col].dtype in [np.float64, np.float32]:
                df[col] = df[col].astype(float)
        except Exception:
            pass
    return df
