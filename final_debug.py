import pandas as pd
import sys
import os
import re

from utils.column_mapper import ColumnMapper

def run_debug():
    log_file = r'd:\ai-lead-conversion-system\debug_log.txt'
    with open(log_file, 'w', encoding='utf-8') as f:
        def log(msg):
            print(msg)
            f.write(msg + '\n')

        log("Loading dataset...")
        try:
            df = pd.read_csv(r'd:\ai-lead-conversion-system\backend\uploads\clean_combined_dataset.csv')
            log(f"Original shape: {df.shape}")
            
            mapper = ColumnMapper()
            log("Running fixed column alignment...")
            
            aligned_df = mapper.align_columns(df)
            log(f"Aligned columns (first 20): {aligned_df.columns.tolist()[:20]}...")
            
            log("Identifying problematic numeric columns...")
            numeric_cols = ['totalvisits', 'timespentonwebsite', 'pageviewspervisit', 
                            'asymmetricactivityscore', 'asymmetricprofilescore']
            
            for col in numeric_cols:
                log(f"Checking column: {col}")
                if col in aligned_df.columns:
                    series_or_df = aligned_df[col]
                    log(f"  Type: {type(series_or_df)}")
                    if isinstance(series_or_df, pd.DataFrame):
                        log(f"  ALERT: Column '{col}' is still a DataFrame! Columns: {series_or_df.columns.tolist()}")
                    
                    try:
                        pd.to_numeric(series_or_df, errors='coerce')
                        log(f"  Result: Success")
                    except Exception as e:
                        log(f"  Result: FAILURE - {str(e)}")
                else:
                    log(f"  Result: Not in dataframe")
            log(f"Aligned columns: {aligned_df.columns.tolist()[:20]}...")
            
            log("Identifying problematic numeric columns...")
            numeric_cols = ['totalvisits', 'timespentonwebsite', 'pageviewspervisit', 
                            'asymmetricactivityscore', 'asymmetricprofilescore']
            
            for col in numeric_cols:
                log(f"Checking column: {col}")
                if col in aligned_df.columns:
                    series_or_df = aligned_df[col]
                    log(f"  Type: {type(series_or_df)}")
                    if isinstance(series_or_df, pd.DataFrame):
                        log(f"  ALERT: Column '{col}' is a DataFrame! Columns: {series_or_df.columns.tolist()}")
                    
                    try:
                        pd.to_numeric(series_or_df, errors='coerce')
                        log(f"  Result: Success")
                    except Exception as e:
                        log(f"  Result: FAILURE - {str(e)}")
                else:
                    log(f"  Result: Not in dataframe")
                    
            log("Debug run finished.")
            
        except Exception as e:
            log(f"CRITICAL ERROR: {str(e)}")
            import traceback
            f.write(traceback.format_exc())

if __name__ == "__main__":
    run_debug()
