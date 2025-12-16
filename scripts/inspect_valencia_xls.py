
import pandas as pd
import sys
import os

# Ensure we can read xls
try:
    file_path = os.path.join("documents", "valencia.xls")
    df = pd.read_excel(file_path)
    print("Columns List:", df.columns.tolist())
    
    print("\nFirst row as dict:")
    print(df.iloc[0].to_dict())
    
except Exception as e:
    print(f"Error reading excel: {e}")
