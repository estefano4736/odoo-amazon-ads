import pandas as pd
import os

file_path = '/Users/estefanomacedo/Documents/antigravity/happy-fermi/data/uploads/Sponsored_Products_Término_de_búsqueda_Reportar.xlsx'
if not os.path.exists(file_path):
    # Try local downloads folder
    file_path = '/Users/estefanomacedo/Downloads/Sponsored_Products_Término_de_búsqueda_Reportar.xlsx'

if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print("Columns in file:")
    print(df.columns.tolist())
    print("\nFirst row:")
    print(df.iloc[0].to_dict())
else:
    print(f"File not found at: {file_path}")
