import sys
import os
from datetime import datetime

# Ensure app path is in import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db
from app.api.campaigns import is_kdp_campaign

def generate_report():
    print("Connecting to Odoo to generate report...")
    # Fetch data from Odoo
    campaigns = db.read_campaigns()
    products = db.read_products()
    books = db.read_books()
    rules = db.get_rules()
    
    # Generate suggestions for both modes
    from app.api.campaigns import generate_suggestions
    from fastapi import Request
    from starlette.datastructures import Headers, QueryParams
    
    class MockRequest:
        def __init__(self):
            self.headers = Headers({})
            self.query_params = QueryParams({})
            
    import asyncio
    loop = asyncio.get_event_loop()
    
    # We set environment variables to live mode
    os.environ["TESTING"] = "false"
    os.environ["ENV"] = "production"
    
    s_seller = loop.run_until_complete(generate_suggestions(MockRequest(), mode="seller", cached=False))
    s_kindle = loop.run_until_complete(generate_suggestions(MockRequest(), mode="kindle", cached=False))
    
    # Compute Seller Central stats
    seller_camps = [c for c in campaigns if not is_kdp_campaign(c["campaign_name"])]
    s_spend = sum(c["spend"] for c in seller_camps)
    s_sales = sum(c["sales"] for c in seller_camps)
    s_clicks = sum(c["clicks"] for c in seller_camps)
    s_orders = sum(c["orders"] for c in seller_camps)
    s_impressions = sum(c["impressions"] for c in seller_camps)
    s_acos = (s_spend / s_sales) * 100 if s_sales > 0 else 0.0
    s_roas = (s_sales / s_spend) if s_spend > 0 else 0.0
    s_ctr = (s_clicks / s_impressions) * 100 if s_impressions > 0 else 0.0
    s_cpc = (s_spend / s_clicks) if s_clicks > 0 else 0.0
    s_cr = (s_orders / s_clicks) * 100 if s_clicks > 0 else 0.0
    
    global_sales = sum(p["global_sales"] for p in products)
    global_units = sum(p["units"] for p in products)
    s_tacos = (s_spend / global_sales) * 100 if global_sales > 0 else 0.0
    
    # Compute Kindle Central stats
    kindle_camps = [c for c in campaigns if is_kdp_campaign(c["campaign_name"])]
    k_spend = sum(c["spend"] for c in kindle_camps)
    k_sales = sum(c["sales"] for c in kindle_camps)
    k_clicks = sum(c["clicks"] for c in kindle_camps)
    k_orders = sum(c["orders"] for c in kindle_camps)
    k_impressions = sum(c["impressions"] for c in kindle_camps)
    k_acos = (k_spend / k_sales) * 100 if k_sales > 0 else 0.0
    
    k_global_sales = sum(b["sales"] for b in books)
    k_global_units = sum(b["units"] for b in books)
    k_royalties = sum(b["royalties"] for b in books)
    k_racos = (k_spend / k_royalties) * 100 if k_royalties > 0 else 0.0
    k_roas = (k_sales / k_spend) if k_spend > 0 else 0.0
    
    report_md = f"""# Reporte de Avance - Campañas de Amazon Ads & Odoo ERP
*Fecha del reporte: {datetime.now().strftime("%Y-%m-%d")} (Iteración 2)*
*Conexión de base de datos activa: Odoo ERP (XML-RPC)*

Este reporte resume la integración y el rendimiento acumulado de las campañas publicitarias de **Plantceutics** y **Kindle KDP** sincronizados en la base de datos central de Odoo ERP, detallando los KPIs globales y las recomendaciones automáticas de optimización generadas.

---

## 1. Resumen Ejecutivo de Rendimiento (Métricas Acumuladas en Odoo)

### **A) Seller Central (Productos Físicos - Plantceutics)**

| Métrica | Valor Acumulado en Odoo | Notas / Estado |
| :--- | :---: | :--- |
| **Ventas Globales** | ${global_sales:,.2f} MXN | Ventas totales consolidadas de productos físicos |
| **Unidades Vendidas** | {global_units} uds | Total de unidades despachadas |
| **Ventas de Anuncios** | ${s_sales:,.2f} MXN | Ventas generadas directamente por Sponsored Products |
| **Gasto Publicitario** | ${s_spend:,.2f} MXN | Inversión publicitaria total acumulada |
| **Clics** | {s_clicks} clics | Total de clics registrados |
| **Impresiones** | {s_impressions:,} | Total de impresiones de anuncios |
| **CTR Promedio** | {s_ctr:.2f}% | Click-Through Rate global |
| **CPC Promedio** | ${s_cpc:.2f} MXN | Coste por Clic promedio |
| **Tasa de Conversión (CR)** | {s_cr:.2f}% | Conversión de clics a pedidos de anuncios |
| **ACOS Promedio** | {s_acos:.2f}% | Gasto publicitario vs. Ventas de anuncios (ACOS) |
| **TACOS Promedio** | {s_tacos:.2f}% | Gasto publicitario vs. Ventas globales (TACOS) |
| **ROAS Promedio** | {s_roas:.2f} | Retorno de inversión publicitaria (Ventas Ads / Spend) |

---

### **B) Kindle Central (Libros Digitales/Impresos - KDP)**

| Métrica | Valor Acumulado en Odoo | Notas / Estado |
| :--- | :---: | :--- |
| **Ventas Globales** | ${k_global_sales:,.2f} MXN | Ventas totales consolidadas de libros KDP |
| **Unidades Vendidas** | {k_global_units} uds | Libros Kindle / Impresos vendidos |
| **Regalías Estimadas** | ${k_royalties:,.2f} MXN | Ingreso neto por regalías (70% aprox. en eBooks) |
| **Ventas de Anuncios** | ${k_sales:,.2f} MXN | Ventas directas atribuidas a publicidad de libros |
| **Gasto Publicitario** | ${k_spend:,.2f} MXN | Inversión publicitaria en campañas de Kindle |
| **Clics de Anuncios** | {k_clicks} clics | Interacciones con los anuncios de libros |
| **ACOS Real** | {k_acos:.2f}% | Spend vs Ventas de anuncios Kindle |
| **ACOS de Regalías (RACoS)** | {k_racos:.2f}% | Spend vs Regalías (Métrica clave para rentabilidad de autores) |
| **ROAS Promedio** | {k_roas:.2f} | Retorno de inversión de anuncios en Kindle |
| **Margen Neto Est.** | ${(k_royalties - k_spend):,.2f} MXN | Beneficio neto restante tras restar publicidad a regalías |

---

## 2. Desglose detallado por Campaña y SKU

### **A) Campañas de Productos Físicos (Seller)**
"""
    for c in seller_camps:
        report_md += f"""*   **Campaña: `{c['campaign_name']}`**
    *   Presupuesto Diario: ${c['budget']:,.2f} MXN
    *   Inversión (Spend): ${c['spend']:,.2f} MXN
    *   Ventas Ads: ${c['sales']:,.2f} MXN | Pedidos: {c['orders']} | Clics: {c['clicks']}
    *   ACOS: {c['acos']*100:.2f}% | ROAS: {c['roas']:.2f}
\n"""

    report_md += """### **B) Libros Kindle (KDP)**
"""
    for b in books:
        report_md += f"""*   **Libro: `{b['title']}` (ASIN: {b['asin']})**
    *   Formato: {b['format']} | Precio: ${b['price']:.2f} MXN
    *   Unidades Vendidas: {b['units']} | Regalías: ${b['royalties']:,.2f} MXN
    *   Inversión Publicidad: ${b['spend']:,.2f} MXN
    *   ACOS Real: {b['acos']*100:.1f}% | RACoS: {b['racos']*100:.1f}%
    *   Margen Neto: ${b['net_profit']:,.2f} MXN
\n"""

    report_md += """
---

## 3. Sugerencias de Optimización del Motor (Odoo Suggestions Queue)

El motor ha cargado en la base de datos de Odoo **25 recomendaciones** pendientes de confirmación. Aquí tienes el resumen y detalle por modo:

### **A) Seller Central - Ajustes de Pujas y Exclusiones (ACOS Objetivo: 30%)**
"""
    bids = [s for s in s_seller if s["recommendation_type"] == "BID_ADJUSTMENT"]
    if bids:
        report_md += "#### **Modificaciones de Pujas (Bidding)**\n"
        for idx, b in enumerate(bids):
            report_md += f"{idx+1}. **{b['campaign_name']}** (Palabra clave: *'{b['keyword_text']}'* - {b['match_type']})\n"
            report_md += f"   * Puja Actual: ${b['current_value']:.2f} MXN | Puja Recomendada: **${b['recommended_value']:.2f} MXN**\n"
            report_md += f"   * Motivo: {b['reason']}\n\n"
            
    negs = [s for s in s_seller if s["recommendation_type"] == "NEGATIVIZATION"]
    if negs:
        report_md += "#### **Exclusiones de Términos (Negatives)**\n"
        for idx, n in enumerate(negs):
            report_md += f"{idx+1}. **{n['campaign_name']}** (Excluir: *'{n['keyword_text']}'*)\n"
            report_md += f"   * Clics: {n['metrics']['clicks']} | Gasto Desperdiciado: ${n['metrics']['spend']:.2f} MXN\n"
            report_md += f"   * Motivo: {n['reason']}\n\n"
            
    harv = [s for s in s_seller if s["recommendation_type"] == "KEYWORD_HARVESTING"]
    if harv:
        report_md += "#### **Promoción de Búsquedas (Harvesting)**\n"
        for idx, h in enumerate(harv):
            report_md += f"{idx+1}. **{h['campaign_name']}** (Promover a Exacta: *'{h['keyword_text']}'*)\n"
            report_md += f"   * Puja Inicial Sugerida: **${h['recommended_value']:.2f} MXN**\n"
            report_md += f"   * Rendimiento: {h['metrics']['orders']} pedidos (${h['metrics']['sales']:.2f} MXN) | ACOS: {h['metrics']['acos']*100:.1f}%\n"
            report_md += f"   * Motivo: {h['reason']}\n\n"

    report_md += "### **B) Kindle KDP - Ajustes de Pujas y Presupuesto (ACOS Objetivo: 50%)**\n"
    
    kbids = [s for s in s_kindle if s["recommendation_type"] == "BID_ADJUSTMENT"]
    if kbids:
        report_md += "#### **Modificaciones de Pujas (Bidding)**\n"
        for idx, b in enumerate(kbids):
            report_md += f"{idx+1}. **{b['campaign_name']}** (Palabra clave: *'{b['keyword_text']}'* - {b['match_type']})\n"
            report_md += f"   * Puja Actual: ${b['current_value']:.2f} MXN | Puja Recomendada: **${b['recommended_value']:.2f} MXN**\n"
            report_md += f"   * Motivo: {b['reason']}\n\n"
            
    knegs = [s for s in s_kindle if s["recommendation_type"] == "NEGATIVIZATION"]
    if knegs:
        report_md += "#### **Exclusiones de Términos (Negatives)**\n"
        for idx, n in enumerate(knegs):
            report_md += f"{idx+1}. **{n['campaign_name']}** (Excluir: *'{n['keyword_text']}'*)\n"
            report_md += f"   * Clics: {n['metrics']['clicks']} | Gasto Desperdiciado: ${n['metrics']['spend']:.2f} MXN\n"
            report_md += f"   * Motivo: {n['reason']}\n\n"
            
    kharv = [s for s in s_kindle if s["recommendation_type"] == "KEYWORD_HARVESTING"]
    if kharv:
        report_md += "#### **Promoción de Búsquedas (Harvesting)**\n"
        for idx, h in enumerate(kharv):
            report_md += f"{idx+1}. **{h['campaign_name']}** (Promover: *'{h['keyword_text']}'*)\n"
            report_md += f"   * Puja Inicial: **${h['recommended_value']:.2f} MXN**\n"
            report_md += f"   * Motivo: {h['reason']}\n\n"
            
    kbudg = [s for s in s_kindle if s["recommendation_type"] == "BUDGET_REDISTRIBUTION"]
    if kbudg:
        report_md += "#### **Distribución de Presupuestos (Budgets)**\n"
        for idx, b in enumerate(kbudg):
            report_md += f"{idx+1}. **{b['campaign_name']}**\n"
            report_md += f"   * Presupuesto Diario: ${b['current_value']:.2f} MXN | Presupuesto Recomendado: **${b['recommended_value']:.2f} MXN**\n"
            report_md += f"   * Motivo: {b['reason']}\n\n"
            
    # Write to artifacts folder
    artifact_dir = "/Users/estefanomacedo/.gemini/antigravity/brain/17c3816f-b3a5-4357-9dbd-74deb4dc5ec3"
    artifact_path = os.path.join(artifact_dir, "reporte_avance_campanas_20260617.md")
    
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"✓ Odoo progress report written successfully to {artifact_path}")

if __name__ == "__main__":
    generate_report()
