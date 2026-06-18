import os
import shutil
import time
import httpx
import pandas as pd
import json

URL = "http://127.0.0.1:8002"
DOWNLOADS_DIR = "/Users/estefanomacedo/Downloads"
WATCHER_TEST_FILE = os.path.join(DOWNLOADS_DIR, "KDP_Watcher_Automation_Test.xlsx")

def create_watcher_test_excel():
    print(f"Creating watcher test Excel in Downloads: {WATCHER_TEST_FILE}")
    data = {
        "ASIN": ["B0GGSD7SM5", "B0GHD59D1Z"],
        "Title": ["La Dieta del ADN", "PRUEBA: La Dieta del ADN"],
        "Quantity": [15, 5],
        "Net Royalty": [75.00, 25.00],
        "Marketplace": ["Amazon.com.mx", "Amazon.com.mx"]
    }
    df = pd.DataFrame(data)
    df.to_excel(WATCHER_TEST_FILE, index=False)
    print("✓ Watcher test file created.")

def test_watcher():
    create_watcher_test_excel()
    
    print("Waiting 12 seconds for the background watcher to process the file...")
    time.sleep(12)
    
    print("Checking KDP report status endpoint...")
    res = httpx.get(f"{URL}/api/campaigns/kdp-report-status")
    assert res.status_code == 200, f"Failed: {res.text}"
    status_data = res.json()
    print("✓ Current KDP report status:")
    print(json.dumps(status_data, indent=2))
    
    # Assertions
    assert status_data["has_report"] is True
    assert status_data["filename"] == "KDP_Watcher_Automation_Test.xlsx"
    assert status_data["total_units"] == 20
    assert status_data["total_royalties"] == 100.0
    
    # Cleanup
    if os.path.exists(WATCHER_TEST_FILE):
        os.remove(WATCHER_TEST_FILE)
        print("✓ Cleaned up Downloads watcher test file.")
        
    uploaded_copy = "./data/uploads/KDP_Watcher_Automation_Test.xlsx"
    if os.path.exists(uploaded_copy):
        os.remove(uploaded_copy)
        print("✓ Cleaned up processed copy from uploads folder.")
        
    print("\n=== WATCHER AUTOMATION TEST PASSED ===")

if __name__ == "__main__":
    try:
        test_watcher()
    except Exception as e:
        print(f"\n✗ Watcher test failed: {e}")
        # Clean up in case of failure
        if os.path.exists(WATCHER_TEST_FILE):
            os.remove(WATCHER_TEST_FILE)
