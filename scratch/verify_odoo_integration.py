import os
import json
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import db

client = TestClient(app)

async def test_integration():
    print("--- 1. Testing Odoo Connection & Clearing Cache ---")
    try:
        uid, models = db.get_connection()
        print(f"Connected to Odoo successfully. UID: {uid}")
    except Exception as e:
        print(f"Failed to connect to Odoo: {e}")
        return

    print("\n--- 2. Clearing existing Odoo tables ---")
    tables_to_clear = [
        'x_amazon_ads_campaign',
        'x_amazon_ads_keyword',
        'x_amazon_ads_search_term',
        'x_amazon_ads_product',
        'x_amazon_ads_book',
        'x_amazon_ads_suggestion',
        'x_amazon_ads_run_history'
    ]
    
    for table in tables_to_clear:
        try:
            ids = models.execute_kw(db.db, uid, db.password, table, 'search', [[]])
            if ids:
                models.execute_kw(db.db, uid, db.password, table, 'unlink', [ids])
                print(f"  Cleared {len(ids)} records from {table}.")
            else:
                print(f"  No records to clear in {table}.")
        except Exception as e:
            print(f"  Error clearing {table}: {e}")

    print("\n--- 3. Processing Seller Central Business Report (SalesDashboard) ---")
    dashboard_file = "/Users/estefanomacedo/Downloads/SalesDashboard-05-06-26.csv mayo y junio.csv"
    if os.path.exists(dashboard_file):
        with open(dashboard_file, "rb") as f:
            res = client.post("/api/bulk/upload-search-terms", files={"file": (os.path.basename(dashboard_file), f, "text/csv")})
            print(f"Upload dashboard status: {res.status_code}")
            print(res.json().get("message", "No message"))
    else:
        print("Dashboard test file not found in Downloads.")

    print("\n--- 4. Processing Sponsored Products Ads Report ---")
    ads_file = "/Users/estefanomacedo/Downloads/Sponsored_Products_Te\u0301rmino_de_bu\u0301squeda_Reportar.xlsx"
    if os.path.exists(ads_file):
        with open(ads_file, "rb") as f:
            res = client.post("/api/bulk/upload-search-terms", files={"file": (os.path.basename(ads_file), f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
            print(f"Upload ads status: {res.status_code}")
            print(f"Keys returned: {list(res.json().keys())}")
    else:
        print("Ads test file not found in Downloads.")

    print("\n--- 5. Verifying Aggregated Odoo Data & Seeding KDP Book ---")
    # Seed a test KDP book to verify x_amazon_ads_book endpoint matches
    try:
        book_vals = {
            'x_asin': 'B0GGSD7SM5',
            'x_title': 'La Dieta del ADN: Aprende a Hackear tus Genes',
            'x_format': 'eBook',
            'x_royalty_pct': 0.70,
            'x_price': 149.00,
            'x_units_sold': 50,
            'x_sponsored_sales': 7450.00,
            'x_royalties_est': 5215.00,
            'x_acos': 0.20,
            'x_racos': 0.28,
            'x_roas': 5.0,
            'x_net_profit': 4000.00
        }
        models.execute_kw(db.db, uid, db.password, 'x_amazon_ads_book', 'create', [book_vals])
        print("Successfully seeded test KDP book record in Odoo.")
    except Exception as e:
        print(f"Error seeding book: {e}")

    campaigns = db.read_campaigns()
    products = db.read_products()
    books = db.read_books()
    keywords = db.read_keywords()
    search_terms = db.read_search_terms()
    
    print(f"Odoo Campaigns read: {len(campaigns)}")
    print(f"Odoo Products read: {len(products)}")
    print(f"Odoo Books read: {len(books)}")
    print(f"Odoo Keywords read: {len(keywords)}")
    print(f"Odoo Search Terms read: {len(search_terms)}")

    print("\n--- 6. Verifying API Metrics Dashboard Endpoint ---")
    res_metrics = client.get("/api/campaigns/metrics")
    print(f"API Metrics Status: {res_metrics.status_code}")
    metrics_json = res_metrics.json()
    print(f"  Organic Sales: ${metrics_json.get('organic_sales'):,.2f}")
    print(f"  Advertising Spend: ${metrics_json.get('spend'):,.2f}")
    print(f"  TACOS: {metrics_json.get('tacos'):.2%}")
    print(f"  Net Payout: ${metrics_json.get('net_payout'):,.2f}")

    print("\n--- 7. Generating Suggestions (Running Optimizer on Real Data) ---")
    res_sug = client.get("/api/campaigns/suggestions")
    print(f"API Suggestions Status: {res_sug.status_code}")
    suggestions = res_sug.json()
    print(f"Generated {len(suggestions)} suggestions from Odoo records.")
    
    # Show first few suggestions
    for idx, s in enumerate(suggestions[:5]):
        print(f"  [{idx+1}] Type: {s['recommendation_type']}, Entity: {s['keyword_text']}, Rec: {s['recommended_value']}, Reason: {s['reason']}")

    # Check that suggestions are cached in Odoo
    odoo_sug_ids = models.execute_kw(db.db, uid, db.password, 'x_amazon_ads_suggestion', 'search', [[]])
    print(f"Confirmed in Odoo cache: {len(odoo_sug_ids)} suggestions found.")

    if suggestions:
        print("\n--- 8. Applying Recommendations ---")
        payload = {"suggestion_ids": [s["id"] for s in suggestions[:3]]}
        res_apply = client.post("/api/campaigns/apply", json=payload)
        print(f"API Apply Status: {res_apply.status_code}")
        print(res_apply.json())

        # Verify Odoo cached suggestions state
        applied_sugs = models.execute_kw(db.db, uid, db.password, 'x_amazon_ads_suggestion', 'search_read', [
            [('x_applied', '=', True)]
        ])
        print(f"Confirmed in Odoo cache: {len(applied_sugs)} suggestions marked as applied.")

if __name__ == "__main__":
    asyncio.run(test_integration())
