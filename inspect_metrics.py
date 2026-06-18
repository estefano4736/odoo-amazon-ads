import json
from datetime import datetime

with open('data/seller_report.json', 'r') as f:
    seller = json.load(f)

with open('data/ads_report.json', 'r') as f:
    ads = json.load(f)

# Dates definition
start_may_june = "2026-05-01"
end_may_june = "2026-06-05"

# 1. Period May-June (5 weeks of May + 1st week of June)
may_june_sales = 0.0
may_june_units = 0
for d, v in seller.get('daily_sales', {}).items():
    if start_may_june <= d <= end_may_june:
        may_june_sales += v.get('sales', 0.0)
        may_june_units += v.get('units', 0)

may_june_spend = 0.0
may_june_clicks = 0
may_june_orders = 0
may_june_sp_sales = 0.0
for d, v in ads.get('daily_ads', {}).items():
    if start_may_june <= d <= end_may_june:
        may_june_spend += v.get('spend', 0.0)
        may_june_clicks += v.get('clicks', 0)
        may_june_orders += v.get('orders', 0)
        may_june_sp_sales += v.get('sales', 0.0)

# 2. Annual (All 2026 data in the file)
annual_sales = seller.get('total_sales', 0.0)
annual_units = seller.get('total_units', 0)

annual_spend = 0.0
annual_clicks = 0
annual_orders = 0
annual_sp_sales = 0.0
for d, v in ads.get('daily_ads', {}).items():
    annual_spend += v.get('spend', 0.0)
    annual_clicks += v.get('clicks', 0)
    annual_orders += v.get('orders', 0)
    annual_sp_sales += v.get('sales', 0.0)

print("--- MAYO Y PRIMER SEMANA DE JUNIO (2026-05-01 al 2026-06-05) ---")
print(f"Global Sales: ${may_june_sales:,.2f} MXN")
print(f"Units: {may_june_units}")
print(f"Ad Spend: ${may_june_spend:,.2f} MXN")
print(f"Ad Sales: ${may_june_sp_sales:,.2f} MXN")
print(f"Clicks: {may_june_clicks}, Orders: {may_june_orders}")

print("\n--- ANUAL (Todo el 2026 disponible) ---")
print(f"Global Sales: ${annual_sales:,.2f} MXN")
print(f"Units: {annual_units}")
print(f"Ad Spend: ${annual_spend:,.2f} MXN")
print(f"Ad Sales: ${annual_sp_sales:,.2f} MXN")
print(f"Clicks: {annual_clicks}, Orders: {annual_orders}")
