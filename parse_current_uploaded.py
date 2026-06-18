import pandas as pd
import os

file_path = 'data/uploads/Sponsored_Products_Término_de_búsqueda_Reportar.xlsx'
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

df = pd.read_excel(file_path)

start_dates = df['Fecha de inicio'].dropna().unique()
end_dates = df['Fecha de finalización'].dropna().unique()

print("Start Dates in report:", start_dates)
print("End Dates in report:", end_dates)
