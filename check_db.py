import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.db import db

creds = db.get_credentials()
if creds:
    print("DATABASE HAS CREDENTIALS!")
    print(f"Client ID: {creds['client_id']}")
    print(f"Region: {creds['region']}")
    print(f"Refresh Token (decrypted): {creds['refresh_token'][:20]}...{creds['refresh_token'][-20:]}")
else:
    print("NO CREDENTIALS IN DATABASE YET.")
