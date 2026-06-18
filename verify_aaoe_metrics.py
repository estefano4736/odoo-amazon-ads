import os
os.environ["TESTING"] = "true"
import json
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import db

client = TestClient(app)

# Credentials Backup for clean testing
CREDS_BACKUP = db.get_credentials()

def cleanup_files():
    if os.path.exists("./data/seller_report.json"):
        os.remove("./data/seller_report.json")
    if os.path.exists("./data/ads_report.json"):
        os.remove("./data/ads_report.json")

def setup_test_db():
    # Delete credentials so the app runs in demo/simulation mode for testing
    with db.get_connection() as conn:
        conn.execute("DELETE FROM credentials")
        conn.commit()

def restore_test_db():
    # Restore the backup credentials
    if CREDS_BACKUP:
        db.save_credentials(
            client_id=CREDS_BACKUP["client_id"],
            client_secret=CREDS_BACKUP["client_secret"],
            refresh_token=CREDS_BACKUP["refresh_token"],
            profile_id=CREDS_BACKUP["profile_id"],
            region=CREDS_BACKUP["region"]
        )

def verify_dashboard_simulated():
    print("\n--- TEST 1: Simulated Dashboard Metrics (No Seller Central Report) ---")
    cleanup_files()
    
    res = client.get("/api/campaigns/metrics")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    print("Dashboard Response:")
    print(json.dumps(data, indent=2))
    
    # Check new fields
    assert "global_sales" in data
    assert "organic_sales" in data
    assert "tacos" in data
    assert "global_roas" in data
    
    # Default global_sales should be sponsored_sales * 2.5
    expected_global = round(data["sales"] * 2.5, 2)
    assert abs(data["global_sales"] - expected_global) < 0.05, f"Expected global_sales {expected_global}, got {data['global_sales']}"
    print("✓ Simulated dashboard metrics verified.")

def verify_products_simulated():
    print("\n--- TEST 2: Simulated Product Breakdown ---")
    res = client.get("/api/campaigns/products")
    assert res.status_code == 200
    products = res.json()
    print(f"Products Response (First Product):")
    print(json.dumps(products[0], indent=2))
    
    for p in products:
        assert "global_sales" in p
        assert "organic_sales" in p
        assert "tacos" in p
        assert "global_roas" in p
        
    print("✓ Simulated product breakdown verified.")

def verify_seller_report_upload():
    print("\n--- TEST 3: Upload Seller Central Business Report ---")
    cleanup_files()
    
    # Create a dummy Seller Central report dataframe
    df_data = {
        "ASIN (secundario)": ["B012345678", "B087654321", "B011223344"],
        "SKU": ["PL-DIG-ENZ-60", "PL-CV-ALG-OM3", "PL-BAL-ADR-90"],
        "Título": ["Super Digestive Enzymes", "Pure Alga Omega 3", "Cortisol Balance"],
        "Sesiones": [150, 100, 80],
        "Unidades pedidas": [30, 15, 10],
        "Ventas de productos": ["$15,000.00 MXN", "$6,500.00 MXN", "$4,800.00 MXN"]
    }
    df = pd.DataFrame(df_data)
    csv_path = "./tests/temp_seller_report.csv"
    df.to_csv(csv_path, index=False)
    
    # Upload via upload-bulk-sheet endpoint (it should auto-detect it!)
    with open(csv_path, "rb") as f:
        res = client.post("/api/bulk/upload-bulk-sheet", files={"file": (os.path.basename(csv_path), f, "text/csv")})
        
    # Clean up temp csv
    if os.path.exists(csv_path):
        os.remove(csv_path)
        
    assert res.status_code == 200, f"Upload failed: {res.text}"
    upload_res = res.json()
    print("Upload Response:")
    print(json.dumps(upload_res, indent=2))
    
    assert upload_res["file_type"] == "seller_business_report"
    assert upload_res["total_sales"] == 26300.0  # 15000 + 6500 + 4800
    
    # Verify DB/File caching
    assert os.path.exists("./data/seller_report.json")
    with open("./data/seller_report.json", "r") as f:
        cached = json.load(f)
    assert cached["total_sales"] == 26300.0
    assert cached["products"]["PL-DIG-ENZ-60"]["sales"] == 15000.0
    
    # Check that dashboard metrics now reflect the actual Seller Central uploaded data!
    print("\n--- TEST 4: Verified Dashboard Metrics (With Seller Central Report) ---")
    res_m = client.get("/api/campaigns/metrics")
    metrics_data = res_m.json()
    print("Dashboard Response (with report):")
    print(json.dumps(metrics_data, indent=2))
    
    assert metrics_data["global_sales"] == 26300.0
    # organic_sales = global_sales (26300) - sponsored_sales (5900) = 20400
    assert metrics_data["organic_sales"] == 20400.0
    
    print("\n--- TEST 5: Verified Product Breakdown (With Seller Central Report) ---")
    res_p = client.get("/api/campaigns/products")
    products_data = res_p.json()
    print("Products Response (with report):")
    print(json.dumps(products_data, indent=2))
    
    # SKU PL-DIG-ENZ-60 should have global_sales = 15000.0
    for p in products_data:
        if p["sku"] == "PL-DIG-ENZ-60":
            assert p["global_sales"] == 15000.0
            # organic_sales = 15000 - sponsored_sales (3850) = 11150
            assert p["organic_sales"] == 11150.0
            # tacos = spend (480) / global_sales (15000) = 0.032
            assert abs(p["tacos"] - 0.032) < 0.005
            
    print("✓ Dynamic metrics update and Seller Central parsing verified successfully!")

if __name__ == "__main__":
    try:
        setup_test_db()
        verify_dashboard_simulated()
        verify_products_simulated()
        verify_seller_report_upload()
    finally:
        restore_test_db()
        cleanup_files()
