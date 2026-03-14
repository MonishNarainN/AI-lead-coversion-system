import pandas as pd
import sys
import os

# Add backend to path
sys.path.append(r'd:\ai-lead-conversion-system\backend')

from utils.column_mapper import ColumnMapper
from services.preprocessing_service import PreprocessingService

def debug_dataset(file_path):
    print(f"Loading {file_path}...")
    try:
        df = pd.read_csv(file_path)
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()[:10]}...")
        
        mapper = ColumnMapper()
        preprocessor = PreprocessingService()
        
        print("Aligning columns...")
        aligned_df = mapper.align_columns(df)
        print(f"Aligned columns: {aligned_df.columns.tolist()}")
        print(f"Aligned types:\n{aligned_df.dtypes}")
        
        print("Starting Preprocessing...")
        # Check for duplicates
        if aligned_df.columns.duplicated().any():
            print(f"WARNING: Duplicate columns found: {aligned_df.columns[aligned_df.columns.duplicated()].tolist()}")
            
        print("Filling missing values...")
        aligned_df = aligned_df.replace('Select', pd.NA)
        
        numeric_cols = ['totalvisits', 'timespentonwebsite', 'pageviewspervisit', 
                        'asymmetricactivityscore', 'asymmetricprofilescore']
        for col in numeric_cols:
            print(f"Processing numeric col: {col}")
            if col in aligned_df.columns:
                data = aligned_df[col]
                print(f"  Type of data for {col}: {type(data)}")
                if isinstance(data, pd.DataFrame):
                    print(f"  CRITICAL: {col} is a DataFrame (duplicate columns?)")
                aligned_df[col] = pd.to_numeric(data, errors='coerce').fillna(0)
            else:
                aligned_df[col] = 0
        
        print("Preprocessing step by step finished!")
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_dataset(r'd:\ai-lead-conversion-system\backend\uploads\clean_combined_dataset.csv')
