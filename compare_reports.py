import os
import sys
import pandas as pd
from app.api.bulk import fuzzy_find_columns

def parse_report(file_path):
    if not os.path.exists(file_path):
        return None, f"File not found: {file_path}"
        
    try:
        if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
            # If it's a bulk sheet, it might have sheets. Let's inspect
            xls = pd.ExcelFile(file_path)
            sp_sheet = None
            for s in xls.sheet_names:
                if "sponsored products" in s.lower() or "sp campaigns" in s.lower():
                    sp_sheet = s
                    break
            if not sp_sheet:
                sp_sheet = xls.sheet_names[0]
            df = pd.read_excel(file_path, sheet_name=sp_sheet)
        else:
            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="latin1")
    except Exception as e:
        return None, f"Error reading file {file_path}: {e}"

    col_mappings = {
        'campaign_name': ['campaign name', 'campaign', 'nombre de la campaña', 'campaña', 'nombre de campaña'],
        'ad_group_name': ['ad group name', 'ad group', 'nombre del grupo de anuncios', 'grupo de anuncios'],
        'customer_search_term': ['customer search term', 'customer search terms', 'search term', 'término de búsqueda de clientes', 'término de búsqueda de cliente', 'término de búsqueda'],
        'clicks': ['clicks', 'clics'],
        'spend': ['spend', 'gasto', 'spent'],
        'sales': ['7 day total sales', 'sales', 'ventas', 'total sales', 'ventas totales de 7 días', 'ventas totales', 'ventas de 7 días'],
        'orders': ['7 day total orders', 'orders', 'conversions', 'pedidos', 'conversiones', 'units sold', 'pedidos totales de 7 días', 'pedidos totales', 'pedidos de 7 días'],
        'impressions': ['impressions', 'impresiones']
    }

    resolved = fuzzy_find_columns(df, col_mappings)
    
    # Check if critical columns are resolved
    required = ["clicks", "spend", "sales"]
    missing = [r for r in required if not resolved[r]]
    if missing:
        return None, f"Missing required columns in report: {', '.join(missing)}. Available columns: {list(df.columns)}"

    total_clicks = 0
    total_spend = 0.0
    total_sales = 0.0
    total_orders = 0
    total_impressions = 0
    
    campaigns_data = {}
    
    for _, row in df.iterrows():
        # Get values safely
        clicks = int(row[resolved['clicks']]) if pd.notna(row[resolved['clicks']]) else 0
        spend = float(row[resolved['spend']]) if pd.notna(row[resolved['spend']]) else 0.0
        sales = float(row[resolved['sales']]) if pd.notna(row[resolved['sales']]) else 0.0
        
        orders = 0
        if resolved['orders'] and pd.notna(row[resolved['orders']]):
            orders = int(row[resolved['orders']])
        elif sales > 0:
            orders = 1
            
        impressions = 0
        if resolved['impressions'] and pd.notna(row[resolved['impressions']]):
            impressions = int(row[resolved['impressions']])
            
        total_clicks += clicks
        total_spend += spend
        total_sales += sales
        total_orders += orders
        total_impressions += impressions
        
        # Group by campaign
        camp_name = str(row[resolved['campaign_name']]) if resolved['campaign_name'] and pd.notna(row[resolved['campaign_name']]) else "Otros"
        if camp_name not in campaigns_data:
            campaigns_data[camp_name] = {
                "clicks": 0,
                "spend": 0.0,
                "sales": 0.0,
                "orders": 0,
                "impressions": 0
            }
        campaigns_data[camp_name]["clicks"] += clicks
        campaigns_data[camp_name]["spend"] += spend
        campaigns_data[camp_name]["sales"] += sales
        campaigns_data[camp_name]["orders"] += orders
        campaigns_data[camp_name]["impressions"] += impressions

    acos = (total_spend / total_sales) * 100 if total_sales > 0 else 0.0
    roas = (total_sales / total_spend) if total_spend > 0 else 0.0
    ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0.0
    cpc = (total_spend / total_clicks) if total_clicks > 0 else 0.0
    cr = (total_orders / total_clicks) * 100 if total_clicks > 0 else 0.0

    summary = {
        "filename": os.path.basename(file_path),
        "total_rows": len(df),
        "impressions": total_impressions,
        "clicks": total_clicks,
        "spend": total_spend,
        "sales": total_sales,
        "orders": total_orders,
        "acos": acos,
        "roas": roas,
        "ctr": ctr,
        "cpc": cpc,
        "cr": cr,
        "campaigns": campaigns_data
    }
    
    return summary, None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compare_reports.py <weekly_report_path> [monthly_report_path]")
        sys.exit(1)
        
    weekly_path = sys.argv[1]
    monthly_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("====================================================")
    print("        AMAZON ADS REPORT COMPARISON ENGINE         ")
    print("====================================================")
    
    weekly_summary, err = parse_report(weekly_path)
    if err:
        print(f"Error parsing weekly report: {err}")
        sys.exit(1)
        
    print(f"\n[REPORT 1: WEEKLY] {weekly_summary['filename']}")
    print(f"  - Rows:        {weekly_summary['total_rows']}")
    print(f"  - Impressions: {weekly_summary['impressions']:,}")
    print(f"  - Clicks:      {weekly_summary['clicks']:,}")
    print(f"  - CTR:         {weekly_summary['ctr']:.2f}%")
    print(f"  - Spend:       ${weekly_summary['spend']:,.2f} MXN")
    print(f"  - CPC:         ${weekly_summary['cpc']:,.2f} MXN")
    print(f"  - Sales:       ${weekly_summary['sales']:,.2f} MXN")
    print(f"  - Orders:      {weekly_summary['orders']:,}")
    print(f"  - CR:          {weekly_summary['cr']:.2f}%")
    print(f"  - ACOS:        {weekly_summary['acos']:.2f}%")
    print(f"  - ROAS:        {weekly_summary['roas']:.2f}")
    
    if monthly_path:
        monthly_summary, err = parse_report(monthly_path)
        if err:
            print(f"Error parsing monthly report: {err}")
            sys.exit(1)
            
        print(f"\n[REPORT 2: MONTHLY] {monthly_summary['filename']}")
        print(f"  - Rows:        {monthly_summary['total_rows']}")
        print(f"  - Impressions: {monthly_summary['impressions']:,}")
        print(f"  - Clicks:      {monthly_summary['clicks']:,}")
        print(f"  - CTR:         {monthly_summary['ctr']:.2f}%")
        print(f"  - Spend:       ${monthly_summary['spend']:,.2f} MXN")
        print(f"  - CPC:         ${monthly_summary['cpc']:,.2f} MXN")
        print(f"  - Sales:       ${monthly_summary['sales']:,.2f} MXN")
        print(f"  - Orders:      {monthly_summary['orders']:,}")
        print(f"  - CR:          {monthly_summary['cr']:.2f}%")
        print(f"  - ACOS:        {monthly_summary['acos']:.2f}%")
        print(f"  - ROAS:        {monthly_summary['roas']:.2f}")
        
        print("\n====================================================")
        print("                 CAMPAIGN COMPARISON                ")
        print("====================================================")
        all_camps = set(list(weekly_summary['campaigns'].keys()) + list(monthly_summary['campaigns'].keys()))
        print(f"{'Campaign Name':<45} | {'Weekly Spend':<12} | {'Weekly Sales':<12} | {'Monthly Spend':<13} | {'Monthly Sales':<13}")
        print("-" * 105)
        for c in sorted(all_camps):
            w_c = weekly_summary['campaigns'].get(c, {"spend": 0.0, "sales": 0.0})
            m_c = monthly_summary['campaigns'].get(c, {"spend": 0.0, "sales": 0.0})
            print(f"{c[:42]:<45} | ${w_c['spend']:10,.2f} | ${w_c['sales']:10,.2f} | ${m_c['spend']:11,.2f} | ${m_c['sales']:11,.2f}")
            
    print("\n====================================================")
