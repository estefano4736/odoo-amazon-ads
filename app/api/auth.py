import os
import httpx
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel
from typing import Optional, List
from app.core.db import db

router = APIRouter(prefix="/api/auth", tags=["auth"])

def check_test_mode(request: Request) -> bool:
    env_header = request.headers.get("x-environment") or request.headers.get("X-Environment")
    is_test_header = env_header == "test"
    is_test_param = request.query_params.get("env") == "test"
    is_env_testing = os.environ.get("ENV") == "testing" or os.environ.get("TESTING") == "true"
    return is_test_header or is_test_param or is_env_testing

class CredentialsPayload(BaseModel):
    client_id: str
    client_secret: str
    refresh_token: str
    region: str = "na"

class ProfileSelectionPayload(BaseModel):
    profile_id: str

# Helper mapping for regional API hosts
REGION_HOSTS = {
    "na": "https://advertising-api.amazon.com",
    "eu": "https://advertising-api-eu.amazon.com",
    "fe": "https://advertising-api-fe.amazon.com"
}

async def get_access_token(client_id: str, client_secret: str, refresh_token: str) -> Optional[str]:
    """Helper to exchange credentials for an access token via LWA OAuth API."""
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
            if response.status_code == 200:
                return response.json().get("access_token")
            return None
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return None

@router.post("/credentials")
async def save_credentials(request: Request, payload: CredentialsPayload, mode: str = Query("seller")):
    test_mode = check_test_mode(request)
    # Clean whitespaces and newlines
    client_id = payload.client_id.strip().replace("\r", "").replace("\n", "").replace(" ", "")
    client_secret = payload.client_secret.strip().replace("\r", "").replace("\n", "").replace(" ", "")
    refresh_token = payload.refresh_token.strip().replace("\r", "").replace("\n", "").replace(" ", "")
    
    is_simulation = (
        not client_id or 
        not client_secret or 
        not refresh_token or 
        client_id.startswith("demo_")
    )
    
    if is_simulation:
        # Save demo credentials
        db.save_credentials(
            client_id="demo_client_id_12345",
            client_secret="demo_secret_abcde",
            refresh_token="demo_refresh_token_xyz",
            profile_id="demo_profile_mx" if mode == "seller" else "demo_profile_kdp_mx",
            region=payload.region,
            mode=mode,
            test_mode=test_mode
        )
        return {
            "status": "success",
            "message": "Demo credentials saved. System is running in Simulation Mode.",
            "mode": "simulation"
        }

    # Verify credentials via Amazon Ads token endpoint
    access_token = await get_access_token(client_id, client_secret, refresh_token)
    if not access_token:
        # Print for local debugging
        print("\n[DEBUG] LWA Authentication Failed. Received values:")
        print(f"  client_id: {client_id}")
        print(f"  client_secret: {client_secret}")
        print(f"  refresh_token: {refresh_token}\n")
        raise HTTPException(
            status_code=400, 
            detail="Failed to authenticate with Amazon LWA. Please verify Client ID, Secret, and Refresh Token."
        )
        
    db.save_credentials(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        region=payload.region,
        mode=mode,
        test_mode=test_mode
    )
    
    return {
        "status": "success",
        "message": "API Credentials saved and validated successfully.",
        "mode": "live"
    }

@router.get("/credentials")
def get_credentials(request: Request, mode: str = Query("seller")):
    test_mode = check_test_mode(request)
    creds = db.get_credentials(mode=mode, test_mode=test_mode)
    if not creds:
        return {
            "configured": False,
            "client_id": "",
            "region": "na",
            "profile_id": None,
            "mode": "simulation"
        }
        
    # Mask values for safety
    cid = creds["client_id"]
    masked_cid = cid[:8] + "..." + cid[-4:] if len(cid) > 12 else "..."
    is_demo = cid.startswith("demo_")
    
    return {
        "configured": True,
        "client_id": masked_cid,
        "region": creds["region"],
        "profile_id": creds["profile_id"],
        "mode": "simulation" if is_demo else "live"
    }

@router.get("/profiles")
async def list_profiles(request: Request, mode: str = Query("seller")):
    test_mode = check_test_mode(request)
    creds = db.get_credentials(mode=mode, test_mode=test_mode)
    if not creds:
        # Default mock profiles if nothing configured yet
        return mock_profiles(mode=mode)
        
    is_demo = creds["client_id"].startswith("demo_")
    if is_demo:
        return mock_profiles(mode=mode)

    # Get active access token
    access_token = await get_access_token(creds["client_id"], creds["client_secret"], creds["refresh_token"])
    if not access_token:
        raise HTTPException(status_code=401, detail="LWA Token validation expired. Please reconfigure credentials.")
        
    # Fetch profiles
    region = creds["region"]
    host = REGION_HOSTS.get(region, REGION_HOSTS["na"])
    url = f"{host}/v2/profiles"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Amazon-Advertising-API-ClientId": creds["client_id"]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch profiles from Amazon: {response.text}")
                # Fallback to simulated profile to prevent dashboard crashes
                return mock_profiles(mode=mode)
        except Exception as e:
            print(f"Error fetching profiles: {e}")
            return mock_profiles(mode=mode)

@router.post("/select-profile")
def select_profile(payload: ProfileSelectionPayload, request: Request, mode: str = Query("seller")):
    test_mode = check_test_mode(request)
    db.update_profile_id(payload.profile_id, mode=mode, test_mode=test_mode)
    return {
        "status": "success",
        "message": f"Active profile set to {payload.profile_id}."
    }

def mock_profiles(mode: str = "seller"):
    if mode == "kindle":
        return [
            {
                "profileId": "demo_profile_kdp_mx",
                "countryCode": "MX",
                "currencyCode": "MXN",
                "timezone": "America/Mexico_City",
                "accountInfo": {
                    "name": "Centrogenica Editorial (Demo)",
                    "type": "kdp"
                }
            },
            {
                "profileId": "demo_profile_kdp_us",
                "countryCode": "US",
                "currencyCode": "USD",
                "timezone": "America/New_York",
                "accountInfo": {
                    "name": "Centrogenica Publishing (Demo)",
                    "type": "kdp"
                }
            }
        ]
    else:
        return [
            {
                "profileId": "demo_profile_mx",
                "countryCode": "MX",
                "currencyCode": "MXN",
                "timezone": "America/Mexico_City",
                "accountInfo": {
                    "name": "Plantceutics México (Demo)",
                    "type": "seller"
                }
            },
            {
                "profileId": "demo_profile_us",
                "countryCode": "US",
                "currencyCode": "USD",
                "timezone": "America/New_York",
                "accountInfo": {
                    "name": "Plantceutics US (Demo)",
                    "type": "seller"
                }
            }
        ]
