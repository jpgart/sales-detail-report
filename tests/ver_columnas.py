import pandas as pd

from sys import path as sys_path
import os
sys_path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from column_name_map import normalize_dataframe_columns, rename_columns_for_readability

excel_path = "/Users/jp/Documents/Famus 3.0/V1/sales_analysis_report_2024-2025v1.xlsx"
df = pd.read_excel(excel_path, sheet_name="Processed_Data")
df = normalize_dataframe_columns(df)
df = rename_columns_for_readability(df)

with open("columnas_processed_data.txt", "w") as f:
    for col in df.columns:
        f.write(col + "\n")
print("Lista de columnas guardada en columnas_processed_data.txt")