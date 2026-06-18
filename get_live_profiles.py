import httpx
import asyncio
import json
from app.core.db import db

async def get_profiles():
    creds = db.get_credentials()
    if not creds:
        print("✗ No credentials found.")
        return
        
    client_id = creds["client_id"]
    client_secret = creds["client_secret"]
    refresh_token = creds["refresh_token"]
    
    token_url = "https://api.amazon.com/auth/o2/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    
    # Increase timeout to 30.0s for slow connections
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            res = await client.post(token_url, data=payload)
            if res.status_code != 200:
                print("✗ Failed to get access token:", res.text)
                return
            access_token = res.json().get("access_token")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Amazon-Advertising-API-ClientId": client_id,
                "Content-Type": "application/json"
            }
            
            # Amazon Ads profiles endpoint
            profiles_url = "https://advertising-api.amazon.com/v2/profiles"
            res_profiles = await client.get(profiles_url, headers=headers)
            if res_profiles.status_code == 200:
                print("✓ Successfully retrieved profiles:")
                profiles = res_profiles.json()
                for p in profiles:
                    print(json.dumps(p, indent=2))
            else:
                print(f"✗ Failed to get profiles: {res_profiles.status_code} - {res_profiles.text}")
        except Exception as e:
            print("✗ Error during profile request:", e)

if __name__ == "__main__":
    asyncio.run(get_profiles())
