import pandas as pd
import json
import os
from datetime import datetime

def process_ads_report_file(file_path: str, output_path: str = 'data/ads_report.json'):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    df = pd.read_excel(file_path)
    
    # Resolve columns dynamically
    col_mappings = {
        "date": ["fecha de inicio", "start date", "fecha"],
        "campaign_name": ["nombre de campaña", "campaign name", "campaign", "campaña"],
        "clicks": ["clics", "clicks"],
        "spend": ["gasto", "spend", "cost", "inversión", "inversion", "costo", "coste"],
        "sales": ["ventas totales de 7 días (€)", "7 day total sales", "sales", "ventas", "ventas totales", "ventas totales de 7 días"],
        "orders": ["pedidos totales de 7 días (#)", "7 day total orders", "orders", "pedidos", "pedidos totales", "pedidos totales de 7 días"],
        "impressions": ["impresiones", "impressions"],
        "ad_group": ["nombre del grupo de anuncios", "ad group name", "ad group", "grupo de anuncios"],
        "targeting": ["segmentación", "targeting", "segmentacion", "palabra clave", "keyword"],
        "match_type": ["tipo de coincidencia", "match type", "match"],
        "search_term": ["término de búsqueda de cliente", "customer search term", "search term", "termino de busqueda"]
    }
    
    resolved = {}
    for key, targets in col_mappings.items():
        found = False
        for target in targets:
            for col in df.columns:
                if target.strip().lower() in str(col).strip().lower():
                    resolved[key] = col
                    found = True
                    break
            if found:
                break
        if not found:
            resolved[key] = None
            
    # If critical columns are missing, we cannot proceed
    critical = ["date", "campaign_name", "spend", "sales"]
    missing = [c for c in critical if not resolved[c]]
    if missing:
        raise ValueError(f"Missing critical columns: {missing}")
        
    campaigns_data = {}
    daily_ads = {}
    
    keywords_agg = {}
    search_terms_agg = {}
    
    for _, row in df.iterrows():
        # Parse date
        raw_date = row[resolved["date"]]
        if pd.isna(raw_date):
            continue
            
        if isinstance(raw_date, datetime):
            date_str = raw_date.strftime("%Y-%m-%d")
        else:
            try:
                date_str = pd.to_datetime(raw_date).strftime("%Y-%m-%d")
            except Exception:
                continue
                
        campaign = str(row[resolved["campaign_name"]]).strip()
        
        # Parse metrics
        clicks = int(row[resolved["clicks"]]) if resolved["clicks"] and pd.notna(row[resolved["clicks"]]) else 0
        impressions = int(row[resolved["impressions"]]) if resolved["impressions"] and pd.notna(row[resolved["impressions"]]) else 0
        
        spend = 0.0
        raw_spend = row[resolved["spend"]]
        if pd.notna(raw_spend):
            if isinstance(raw_spend, (int, float)):
                spend = float(raw_spend)
            else:
                spend = float(str(raw_spend).replace("$", "").replace("€", "").replace(",", "").strip())
                
        sales = 0.0
        raw_sales = row[resolved["sales"]]
        if pd.notna(raw_sales):
            if isinstance(raw_sales, (int, float)):
                sales = float(raw_sales)
            else:
                sales = float(str(raw_sales).replace("$", "").replace("€", "").replace(",", "").strip())
                
        orders = int(row[resolved["orders"]]) if resolved["orders"] and pd.notna(row[resolved["orders"]]) else (1 if sales > 0 else 0)
        
        # Group by campaign
        if campaign not in campaigns_data:
            campaigns_data[campaign] = {
                "spend": 0.0,
                "sales": 0.0,
                "clicks": 0,
                "orders": 0,
                "impressions": 0,
                "daily": {}
            }
            
        campaigns_data[campaign]["spend"] += spend
        campaigns_data[campaign]["sales"] += sales
        campaigns_data[campaign]["clicks"] += clicks
        campaigns_data[campaign]["orders"] += orders
        campaigns_data[campaign]["impressions"] += impressions
        
        if date_str not in campaigns_data[campaign]["daily"]:
            campaigns_data[campaign]["daily"][date_str] = {
                "spend": 0.0,
                "sales": 0.0,
                "clicks": 0,
                "orders": 0,
                "impressions": 0
            }
        campaigns_data[campaign]["daily"][date_str]["spend"] += spend
        campaigns_data[campaign]["daily"][date_str]["sales"] += sales
        campaigns_data[campaign]["daily"][date_str]["clicks"] += clicks
        campaigns_data[campaign]["daily"][date_str]["orders"] += orders
        campaigns_data[campaign]["daily"][date_str]["impressions"] += impressions
        
        # Global daily ads metrics
        if date_str not in daily_ads:
            daily_ads[date_str] = {
                "spend": 0.0,
                "sales": 0.0,
                "clicks": 0,
                "orders": 0,
                "impressions": 0
            }
        daily_ads[date_str]["spend"] += spend
        daily_ads[date_str]["sales"] += sales
        daily_ads[date_str]["clicks"] += clicks
        daily_ads[date_str]["orders"] += orders
        daily_ads[date_str]["impressions"] += impressions
        
        # Parse ad group, targeting, match type, search term details
        ad_group = str(row[resolved["ad_group"]]).strip() if resolved["ad_group"] and pd.notna(row[resolved["ad_group"]]) else "default"
        targeting = str(row[resolved["targeting"]]).strip() if resolved["targeting"] and pd.notna(row[resolved["targeting"]]) else ""
        m_type = str(row[resolved["match_type"]]).strip() if resolved["match_type"] and pd.notna(row[resolved["match_type"]]) else ""
        s_term = str(row[resolved["search_term"]]).strip() if resolved["search_term"] and pd.notna(row[resolved["search_term"]]) else ""
        
        if targeting:
            kw_key = (campaign, ad_group, targeting, m_type)
            if kw_key not in keywords_agg:
                keywords_agg[kw_key] = {
                    "campaign_name": campaign,
                    "ad_group_name": ad_group,
                    "keyword_text": targeting,
                    "match_type": m_type,
                    "clicks": 0,
                    "spend": 0.0,
                    "sales": 0.0,
                    "orders": 0
                }
            keywords_agg[kw_key]["clicks"] += clicks
            keywords_agg[kw_key]["spend"] += spend
            keywords_agg[kw_key]["sales"] += sales
            keywords_agg[kw_key]["orders"] += orders
            
        if s_term:
            st_key = (campaign, ad_group, s_term)
            if st_key not in search_terms_agg:
                search_terms_agg[st_key] = {
                    "campaign_name": campaign,
                    "ad_group_name": ad_group,
                    "search_term": s_term,
                    "clicks": 0,
                    "spend": 0.0,
                    "sales": 0.0,
                    "orders": 0
                }
            search_terms_agg[st_key]["clicks"] += clicks
            search_terms_agg[st_key]["spend"] += spend
            search_terms_agg[st_key]["sales"] += sales
            search_terms_agg[st_key]["orders"] += orders
            
    report_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "filename": os.path.basename(file_path),
        "total_spend": sum(c["spend"] for c in campaigns_data.values()),
        "total_sales": sum(c["sales"] for c in campaigns_data.values()),
        "total_clicks": sum(c["clicks"] for c in campaigns_data.values()),
        "total_orders": sum(c["orders"] for c in campaigns_data.values()),
        "total_impressions": sum(c["impressions"] for c in campaigns_data.values()),
        "daily_ads": daily_ads,
        "campaigns": campaigns_data
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)
        
    print(f"✓ Successfully processed ads report. Total Spend: ${report_data['total_spend']:,.2f} MXN")

    # Write to Odoo Database
    try:
        from app.core.db import db
        
        # 1. Synchronize Campaigns
        campaigns_list = []
        for c_name, c_info in campaigns_data.items():
            campaigns_list.append({
                "campaign_id": c_name,
                "campaign_name": c_name,
                "adType": "sp",
                "budget": 500.0,
                "spend": c_info["spend"],
                "sales": c_info["sales"],
                "orders": c_info["orders"],
                "clicks": c_info["clicks"],
                "impressions": c_info["impressions"]
            })
        db.write_campaigns(campaigns_list)

        # 2. Synchronize Keywords & Search Terms
        keywords_list = []
        for kw_key, kw_val in keywords_agg.items():
            clicks = kw_val["clicks"]
            spend = kw_val["spend"]
            kw_val["bid"] = round(spend / clicks, 2) if clicks > 0 else 0.50
            keywords_list.append(kw_val)
            
        search_terms_list = list(search_terms_agg.values())
        
        db.write_keywords(keywords_list)
        db.write_search_terms(search_terms_list)

        # 3. Synchronize Products Ads Performance
        product_map = {
            "PL-DIG-ENZ-60": {
                "sku": "PL-DIG-ENZ-60",
                "name": "Super Digestive Enzymes (60 Caps)",
                "asin": "B012345678",
                "category": "Digestivo",
                "campaign_keywords": ["digestive", "enzimas", "enz"]
            },
            "PL-CV-ALG-OM3": {
                "sku": "PL-CV-ALG-OM3",
                "name": "Pure Alga Omega 3 (120ml)",
                "asin": "B087654321",
                "category": "Cardiovascular",
                "campaign_keywords": ["omega", "alg", "cv", "pure alga"]
            },
            "PL-BAL-ADR-90": {
                "sku": "PL-BAL-ADR-90",
                "name": "Adrenal Health & Cortisol Balance",
                "asin": "B011223344",
                "category": "Balance & Estrés",
                "campaign_keywords": ["adrenal", "cortisol", "adr", "balance"]
            }
        }
        
        sku_to_product = {}
        for sku, p_info in product_map.items():
            sku_to_product[sku] = {
                "sku": sku,
                "name": p_info["name"],
                "asin": p_info["asin"],
                "category": p_info["category"],
                "spend": 0.0,
                "sales": 0.0,
                "clicks": 0,
                "units": 0
            }
            
        for c_name, metrics in campaigns_data.items():
            c_name_lower = c_name.lower()
            mapped = False
            for sku, p_info in product_map.items():
                for kw in p_info["campaign_keywords"]:
                    if kw in c_name_lower:
                        if kw == "balance" and "predeterminados" in c_name_lower:
                            continue
                        sku_to_product[sku]["spend"] += metrics["spend"]
                        sku_to_product[sku]["sales"] += metrics["sales"]
                        sku_to_product[sku]["clicks"] += metrics["clicks"]
                        sku_to_product[sku]["units"] += metrics["orders"]
                        mapped = True
                        break
                if mapped:
                    break
            if not mapped:
                import re
                asin_match = re.search(r'B[0-9A-Z]{9}', c_name)
                asin = asin_match.group(0) if asin_match else c_name
                sku = asin
                if sku not in sku_to_product:
                    name = f"Producto {sku}"
                    category = "Otros"
                    if "B0CKJC1MZZ" in sku:
                        name = "Ad Ready Balance (B0CKJC1MZZ)"
                        category = "Balance & Estrés"
                    elif "B0CWN13K56" in sku:
                        name = "Suplemento Wellness (B0CWN13K56)"
                        category = "Suplemento"
                    sku_to_product[sku] = {
                        "sku": sku,
                        "name": name,
                        "asin": asin,
                        "category": category,
                        "spend": 0.0,
                        "sales": 0.0,
                        "clicks": 0,
                        "units": 0
                    }
                sku_to_product[sku]["spend"] += metrics["spend"]
                sku_to_product[sku]["sales"] += metrics["sales"]
                sku_to_product[sku]["clicks"] += metrics["clicks"]
                sku_to_product[sku]["units"] += metrics["orders"]
                
        db.write_products(list(sku_to_product.values()))
        print("[Odoo DB] Synchronized campaigns and products ads metrics from ads report.")
        
        # 4. Send Odoo Discuss Notification
        summary_html = f"""
        <p>Se ha procesado e ingestado un nuevo reporte de anuncios <b>Sponsored Products</b> con éxito:</p>
        <ul>
            <li><b>Archivo:</b> <code>{os.path.basename(file_path)}</code></li>
            <li><b>Campañas Sincronizadas:</b> {len(campaigns_list)}</li>
            <li><b>Palabras Clave Cargadas:</b> {len(keywords_list)}</li>
            <li><b>Términos de Búsqueda Cargados:</b> {len(search_terms_list)}</li>
            <li><b>Inversión Publicitaria Total:</b> ${report_data['total_spend']:,.2f} MXN</li>
            <li><b>Ventas por Anuncios Totales:</b> ${report_data['total_sales']:,.2f} MXN</li>
        </ul>
        <p>El reporte está cargado y listo en Odoo. El motor de optimización ya cuenta con datos actualizados para generar sugerencias de ajustes.</p>
        """
        db.post_discuss_message(
            channel_name="Amazon Ads Optimization",
            subject="Reporte de Anuncios Ingestado con Éxito",
            message_html=summary_html
        )
        
    except Exception as db_err:
        print(f"[Odoo DB] Error writing ads metrics or sending notification: {db_err}")

    return report_data

if __name__ == "__main__":
    file_path = 'data/uploads/Sponsored_Products_Término_de_búsqueda_Reportar.xlsx'
    output_path = 'data/ads_report.json'
    process_ads_report_file(file_path, output_path)
