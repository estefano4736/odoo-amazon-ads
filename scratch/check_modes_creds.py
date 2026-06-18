import asyncio
from app.core.db import db

async def check_creds():
    print("--- Checking Odoo Credentials for Amazon Ads ---")
    try:
        uid, models = db.get_connection()
        print(f"Connected to Odoo successfully. UID: {uid}")
        
        # Read all credentials from the Odoo model
        records = models.execute_kw(db.db, uid, db.password, 'x_amazon_ads_credentials', 'search_read', [[]])
        print(f"\nFound {len(records)} credentials records in Odoo:")
        for r in records:
            print(f"- ID: {r.get('id')}")
            print(f"  Name: {r.get('x_name')}")
            print(f"  Mode: {r.get('x_mode')}")
            print(f"  Region: {r.get('x_region')}")
            client_id = r.get('x_client_id') or ""
            print(f"  Client ID (masked): {client_id[:8]}...{client_id[-4:] if len(client_id) > 12 else ''}")
            print(f"  Profile ID: {r.get('x_profile_id')}")
            print(f"  Last Updated: {r.get('write_date')}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error querying Odoo: {e}")

if __name__ == "__main__":
    asyncio.run(check_creds())
