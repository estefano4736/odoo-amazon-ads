import os
import shutil
import json
import csv
from datetime import datetime

# Source paths in Downloads
downloads_dir = '/Users/estefanomacedo/Downloads'
files_to_copy = [
    'SalesDashboard-05-06-26.csv anual.csv',
    'SalesDashboard-05-06-26.csv mayo y junio.csv',
    'SalesDashboard-05-06-26.csv semanal.csv',
    'Sponsored_Products_Término_de_búsqueda_Reportar.xlsx'
]

target_dir = './data/uploads'
os.makedirs(target_dir, exist_ok=True)

# Copy files
for filename in files_to_copy:
    src = os.path.join(downloads_dir, filename)
    dst = os.path.join(target_dir, filename)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"✓ Copied {filename} to {dst}")
    else:
        print(f"✗ Source file not found: {src}")

# Process Ads Report
from process_ads_report import process_ads_report_file
ads_xlsx = os.path.join(target_dir, 'Sponsored_Products_Término_de_búsqueda_Reportar.xlsx')
if os.path.exists(ads_xlsx):
    process_ads_report_file(ads_xlsx)
    print("✓ Successfully processed ads report.")
else:
    print("✗ Ads report file not found for processing.")

# Process Annual Sales Dashboard as the default active report
from app.api.bulk import run_sales_dashboard_process_from_file
import asyncio

annual_csv = os.path.join(target_dir, 'SalesDashboard-05-06-26.csv anual.csv')
if os.path.exists(annual_csv):
    # Run the async parser
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(run_sales_dashboard_process_from_file(annual_csv, 'SalesDashboard-05-06-26.csv anual.csv'))
    print(f"✓ Successfully processed annual seller report: {res}")
else:
    print("✗ Annual CSV not found for processing.")
