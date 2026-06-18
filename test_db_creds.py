import httpx
import asyncio
from app.core.db import db

async def test_creds():
    creds = db.get_credentials()
    if not creds:
        print("✗ No credentials found in database.")
        return
        
    client_id = creds["client_id"]
    client_secret = creds["client_secret"]
    refresh_token = creds["refresh_token"]
    
    print("Testing DB Credentials:")
    print(f"  Client ID: {client_id}")
    print(f"  Client Secret: {client_secret}")
    print(f"  Refresh Token length: {len(refresh_token)}")
    print(f"  Refresh Token starts with: {refresh_token[:20]}...")
    
    url = "https://api.amazon.com/auth/o2/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=payload, timeout=10.0)
            print(f"\nAmazon Response Code: {response.status_code}")
            if response.status_code == 200:
                res_json = response.json()
                print("✓ SUCCESS: Valid credentials! Access token retrieved.")
                print(f"Access Token starts with: {res_json.get('access_token')[:15]}...")
            else:
                print("✗ FAILED: Amazon returned an error:")
                print(response.text)
        except Exception as e:
            print(f"✗ Exception occurred during token request: {e}")

if __name__ == "__main__":
    asyncio.run(test_creds())
