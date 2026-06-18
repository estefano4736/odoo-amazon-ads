import httpx
import asyncio
from app.core.db import db

async def test_ads_api():
    creds = db.get_credentials()
    if not creds:
        print("✗ No credentials found.")
        return
        
    client_id = creds["client_id"]
    client_secret = creds["client_secret"]
    refresh_token = creds["refresh_token"]
    profile_id = creds["profile_id"]
    
    # 1. Refresh token to get access token
    token_url = "https://api.amazon.com/auth/o2/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(token_url, data=payload)
            if res.status_code != 200:
                print("✗ Failed to get access token:", res.text)
                return
            access_token = res.json().get("access_token")
            print("✓ Successfully fetched access token.")
            
            # 2. Setup Headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Amazon-Advertising-API-ClientId": client_id,
                "Amazon-Advertising-API-Scope": str(profile_id),
                "Content-Type": "application/vnd.spcampaign.v3+json",
                "Accept": "application/vnd.spCampaign.v3+json"
            }
            
            host = "https://advertising-api.amazon.com"

            # Try POST /sp/campaigns/list (v3 list endpoint)
            print(f"\nTrying POST {host}/sp/campaigns/list...")
            payload_list = {
                "maxResults": 50
            }
            res_camps_post = await client.post(f"{host}/sp/campaigns/list", headers=headers, json=payload_list)
            print("POST Response Code:", res_camps_post.status_code)
            if res_camps_post.status_code == 200:
                res_data = res_camps_post.json()
                print("✓ Successfully retrieved campaigns via POST:")
                print(json.dumps(res_data, indent=2)[:1500])
            else:
                print("POST Response text:", res_camps_post.text)
                
        except Exception as e:
            print("✗ Exception:", e)

if __name__ == "__main__":
    import json
    asyncio.run(test_ads_api())
