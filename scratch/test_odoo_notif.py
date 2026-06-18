import os
import xmlrpc.client
from dotenv import load_dotenv

env_path = "/Users/estefanomacedo/Documents/antigravity/happy-fermi/.env"
load_dotenv(env_path)

url = os.getenv("ODOO_URL")
db_name = os.getenv("ODOO_DB")
username = os.getenv("ODOO_USER")
password = os.getenv("ODOO_API_KEY")

try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db_name, username, password, {})
    if uid:
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Search for channel named "Amazon Ads Optimization"
        channel_ids = models.execute_kw(db_name, uid, password, 'discuss.channel', 'search', [
            [('name', '=', 'Amazon Ads Optimization')]
        ])
        
        if channel_ids:
            channel_id = channel_ids[0]
            print(f"Found existing channel ID: {channel_id}")
        else:
            # Create a new discuss channel
            # In Odoo, discuss.channel can be created
            channel_id = models.execute_kw(db_name, uid, password, 'discuss.channel', 'create', [{
                'name': 'Amazon Ads Optimization',
                'channel_type': 'channel',
            }])
            print(f"Created new channel ID: {channel_id}")
            
        # Try to post a test message
        msg_id = models.execute_kw(db_name, uid, password, 'discuss.channel', 'message_post', [channel_id], {
            'body': '<h3>Recomendaciones de Optimización de Amazon Ads</h3><p>Se han generado <b>3 nuevos ajustes de pujas</b> y <b>1 negativización</b>.</p><p;><a href="/web#menu_id=100" target="_blank">Ver detalles en el dashboard</a></p>',
            'message_type': 'comment',
            'subtype_xmlid': 'mail.mt_comment'
        })
        print(f"Message posted successfully, ID: {msg_id}")
        
    else:
        print("Auth failed.")
except Exception as e:
    print(f"Error: {e}")
