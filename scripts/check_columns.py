import pandas as pd

file_path = "c:/Users/Alvaro/Documents/GitHub/Anti-Bullyng_app/documents/valencia.xls"
try:
    df = pd.read_excel(file_path)
    print("Columns found:")
    print(df.columns.tolist())
    print("\nFirst row sample:")
    print(df.head(1).to_dict())
except Exception as e:
    print(f"Error reading Excel: {e}")
