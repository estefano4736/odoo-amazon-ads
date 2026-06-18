import sys
import json
import urllib.request
import urllib.parse
from app.core.db import db

def run_exchange():
    # 1. Fetch existing credentials from the SQLite DB
    creds = db.get_credentials()
    if not creds:
        print("✗ No credentials found in database to perform exchange.")
        return
        
    client_id = creds["client_id"]
    client_secret = creds["client_secret"]
    code = "ANosxDQShCGIDZWXodFM"
    redirect_uri = "http://127.0.0.1:8001/"
    
    print(f"Exchanging code using:")
    print(f"  - Client ID: {client_id[:15]}...")
    print(f"  - Code: {code}")
    print(f"  - Redirect URI: {redirect_uri}")
    
    url = "https://api.amazon.com/auth/o2/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            refresh_token = res_data.get('refresh_token')
            access_token = res_data.get('access_token')
            print("\n=========================================================")
            print("✓ SUCCESS: Exchanged code for tokens.")
            print(f"  - Refresh Token starts with: {refresh_token[:15]}...")
            print("=========================================================")
            
            # Save the new refresh token to the database
            db.save_credentials(
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=refresh_token,
                profile_id=creds.get("profile_id"),
                region=creds.get("region", "na")
            )
            print("✓ Saved new Refresh Token to database.")
            
    except urllib.error.HTTPError as e:
        print(f"\n✗ ERROR from Amazon (HTTP {e.code}):")
        print(e.read().decode("utf-8"))
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

if __name__ == "__main__":
    run_exchange()
