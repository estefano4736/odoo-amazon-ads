import pandas as pd
import json
from app.core.rules import identify_negatives
from app.core.db import db
from app.api.bulk import fuzzy_find_columns

rules = db.get_rules()
file_path = 'data/uploads/Sponsored_Products_Término_de_búsqueda_Reportar.xlsx'
df = pd.read_excel(file_path)

col_mappings = {
    'campaign_name': ['campaign name', 'campaign', 'nombre de la campaña', 'campaña', 'nombre de campaña'],
    'ad_group_name': ['ad group name', 'ad group', 'nombre del grupo de anuncios', 'grupo de anuncios'],
    'customer_search_term': ['customer search term', 'customer search terms', 'search term', 'término de búsqueda de clientes', 'término de búsqueda de cliente', 'término de búsqueda'],
    'clicks': ['clicks', 'clics'],
    'spend': ['spend', 'gasto', 'spent'],
    'sales': ['7 day total sales', 'sales', 'ventas', 'total sales', 'ventas totales de 7 días', 'ventas totales'],
    'orders': ['7 day total orders', 'orders', 'conversions', 'pedidos', 'conversiones', 'units sold', 'pedidos totales de 7 días', 'pedidos totales']
}

resolved = fuzzy_find_columns(df, col_mappings)
search_terms_list = []

for _, row in df.iterrows():
    st_text = str(row[resolved['customer_search_term']]) if pd.notna(row[resolved['customer_search_term']]) else ''
    if not st_text or st_text.startswith('*') or st_text.strip() == '':
        continue
    
    # Extract orders index or default to 0
    orders = 0
    if resolved['orders'] and pd.notna(row[resolved['orders']]):
        orders = int(row[resolved['orders']])
    elif resolved['sales'] and pd.notna(row[resolved['sales']]) and float(row[resolved['sales']]) > 0:
        orders = 1
        
    search_terms_list.append({
        'campaign_name': str(row[resolved['campaign_name']]) if resolved['campaign_name'] and pd.notna(row[resolved['campaign_name']]) else 'Bulk Campaign',
        'ad_group_name': str(row[resolved['ad_group_name']]) if resolved['ad_group_name'] and pd.notna(row[resolved['ad_group_name']]) else 'Bulk Ad Group',
        'customer_search_term': st_text,
        'clicks': int(row[resolved['clicks']]) if pd.notna(row[resolved['clicks']]) else 0,
        'spend': float(row[resolved['spend']]) if pd.notna(row[resolved['spend']]) else 0.0,
        'sales': float(row[resolved['sales']]) if pd.notna(row[resolved['sales']]) else 0.0,
        'orders': orders,
    })

negatives = identify_negatives(search_terms_list, rules['max_spend_no_sales'], rules['min_clicks_no_sales'])
print(f'TOTAL_NEGATIVAS:{len(negatives)}')
for idx, n in enumerate(negatives):
    print(f'{idx+1}. Term: {n["keyword_text"]} | Clicks: {n["metrics"]["clicks"]} | Spend: ${n["metrics"]["spend"]:.2f} | Campaign: {n["campaign_name"]} | Reason: {n["reason"]}')
