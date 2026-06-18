import os
import xmlrpc.client

def get_connection():
    # Simple manual parser for .env if python-dotenv is not installed
    env_vars = {}
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_vars[k.strip()] = v.strip()
    
    url = env_vars.get("ODOO_URL") or os.environ.get("ODOO_URL")
    db = env_vars.get("ODOO_DB") or os.environ.get("ODOO_DB")
    username = env_vars.get("ODOO_USER") or os.environ.get("ODOO_USER")
    password = env_vars.get("ODOO_API_KEY") or os.environ.get("ODOO_API_KEY")
    
    if not all([url, db, username, password]):
        raise ValueError("Missing Odoo connection details in .env file or environment variables.")
        
    print(f"Connecting to Odoo at {url}...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise PermissionError("Failed to authenticate with Odoo. Check your username and API key.")
        
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    return url, db, username, password, uid, models
