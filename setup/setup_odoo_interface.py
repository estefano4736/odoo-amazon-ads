import sys
import os
from odoo_client import get_connection

def main():
    try:
        url, db, username, password, uid, models = get_connection()
        print(f"Connected to Odoo: {url}")

        # Helper to find model ID
        def get_model_id(model_name):
            res = models.execute_kw(db, uid, password, 'ir.model', 'search', [[('model', '=', model_name)]])
            return res[0] if res else None

        # ----------------------------------------------------
        # 1. Find Module Category (Sales or Marketing)
        # ----------------------------------------------------
        print("\n--- Finding Module Category ---")
        category_id = None
        category_ids = models.execute_kw(db, uid, password, 'ir.module.category', 'search', [
            ['|', ('name', '=', 'Sales'), ('name', '=', 'Marketing')]
        ])
        if category_ids:
            category_id = category_ids[0]
            print(f"Using category ID: {category_id}")
        else:
            print("No category 'Sales' or 'Marketing' found. Group will be created without category.")

        # ----------------------------------------------------
        # 2. Create Security Groups
        # ----------------------------------------------------
        print("\n--- Setting up Security Groups ---")
        # Group: Usuario
        user_group_ids = models.execute_kw(db, uid, password, 'res.groups', 'search', [
            [('name', '=', 'Amazon Ads / Usuario')]
        ])
        if user_group_ids:
            user_group_id = user_group_ids[0]
            print(f"Group 'Amazon Ads / Usuario' already exists (ID: {user_group_id}).")
        else:
            user_group_vals = {
                'name': 'Amazon Ads / Usuario',
            }
            user_group_id = models.execute_kw(db, uid, password, 'res.groups', 'create', [user_group_vals])
            print(f"Created Security Group 'Amazon Ads / Usuario' (ID: {user_group_id}).")

        # Group: Administrador
        admin_group_ids = models.execute_kw(db, uid, password, 'res.groups', 'search', [
            [('name', '=', 'Amazon Ads / Administrador')]
        ])
        if admin_group_ids:
            admin_group_id = admin_group_ids[0]
            print(f"Group 'Amazon Ads / Administrador' already exists (ID: {admin_group_id}).")
        else:
            admin_group_vals = {
                'name': 'Amazon Ads / Administrador',
                'implied_ids': [[6, 0, [user_group_id]]] # Inherits User permissions
            }
            admin_group_id = models.execute_kw(db, uid, password, 'res.groups', 'create', [admin_group_vals])
            print(f"Created Security Group 'Amazon Ads / Administrador' (ID: {admin_group_id}).")

        # ----------------------------------------------------
        # 3. Create Access Rights (ir.model.access)
        # ----------------------------------------------------
        print("\n--- Setting up Access Control Lists (ACLs) ---")
        
        target_models = [
            'x_amazon_ads_credentials',
            'x_amazon_ads_rules',
            'x_amazon_ads_campaign',
            'x_amazon_ads_keyword',
            'x_amazon_ads_search_term',
            'x_amazon_ads_product',
            'x_amazon_ads_book',
            'x_amazon_ads_suggestion',
            'x_amazon_ads_run_history'
        ]

        def create_acl(name, model_name, group_id, r, w, c, u):
            m_id = get_model_id(model_name)
            if not m_id:
                print(f"  Warning: Model {model_name} not found, skipping ACL.")
                return
                
            # Check if ACL already exists
            existing = models.execute_kw(db, uid, password, 'ir.model.access', 'search', [
                [('model_id', '=', m_id), ('group_id', '=', group_id)]
            ])
            if existing:
                print(f"  ACL for '{model_name}' and group {group_id} already exists. Overwriting...")
                models.execute_kw(db, uid, password, 'ir.model.access', 'write', [
                    existing, {
                        'perm_read': r,
                        'perm_write': w,
                        'perm_create': c,
                        'perm_unlink': u
                    }
                ])
                return existing[0]

            acl_vals = {
                'name': name,
                'model_id': m_id,
                'group_id': group_id,
                'perm_read': r,
                'perm_write': w,
                'perm_create': c,
                'perm_unlink': u
            }
            acl_id = models.execute_kw(db, uid, password, 'ir.model.access', 'create', [acl_vals])
            print(f"  Created ACL for '{model_name}' (ID: {acl_id}).")
            return acl_id

        # Admin: Full permissions on all models
        print("  Assigning full permissions for Amazon Ads / Administrador...")
        for m in target_models:
            create_acl(f"access_{m}_admin", m, admin_group_id, True, True, True, True)

        # User: Read-only permissions on reporting models (NO access to credentials/rules)
        print("  Assigning read-only permissions for Amazon Ads / Usuario...")
        reporting_models = [
            'x_amazon_ads_campaign',
            'x_amazon_ads_keyword',
            'x_amazon_ads_search_term',
            'x_amazon_ads_product',
            'x_amazon_ads_book',
            'x_amazon_ads_suggestion',
            'x_amazon_ads_run_history'
        ]
        for m in reporting_models:
            create_acl(f"access_{m}_user", m, user_group_id, True, False, False, False)

        # ----------------------------------------------------
        # 4. Create Window/URL Action and Menu
        # ----------------------------------------------------
        print("\n--- Setting up Menu and URL Action ---")
        
        # Check if URL action exists
        action_name = "Amazon Ads Optimizer"
        existing_action = models.execute_kw(db, uid, password, 'ir.actions.act_url', 'search', [
            [('name', '=', action_name)]
        ])
        
        # URL of our service (local or cloud)
        env_vars = {}
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        env_vars[k.strip()] = v.strip()
                        
        dashboard_url = os.environ.get("DASHBOARD_URL") or env_vars.get("DASHBOARD_URL") or "http://localhost:8001"
        print(f"Configuring Odoo URL Action with: {dashboard_url}")
        
        action_vals = {
            'name': action_name,
            'url': dashboard_url,
            'target': 'self' # Opens inside Odoo's frame
        }
        
        if existing_action:
            action_id = existing_action[0]
            print(f"URL Action already exists (ID: {action_id}). Updating...")
            models.execute_kw(db, uid, password, 'ir.actions.act_url', 'write', [[action_id], action_vals])
        else:
            action_id = models.execute_kw(db, uid, password, 'ir.actions.act_url', 'create', [action_vals])
            print(f"Created URL Action '{action_name}' (ID: {action_id}).")

        # Create root menu item pointing to this action
        existing_menu = models.execute_kw(db, uid, password, 'ir.ui.menu', 'search', [
            [('name', '=', 'Amazon Ads')]
        ])
        
        menu_vals = {
            'name': 'Amazon Ads',
            'action': f"ir.actions.act_url,{action_id}",
            'sequence': 100,
        }
        
        if existing_menu:
            menu_id = existing_menu[0]
            print(f"Menu item already exists (ID: {menu_id}). Updating...")
            models.execute_kw(db, uid, password, 'ir.ui.menu', 'write', [[menu_id], menu_vals])
        else:
            menu_id = models.execute_kw(db, uid, password, 'ir.ui.menu', 'create', [menu_vals])
            print(f"Created Root Menu 'Amazon Ads' (ID: {menu_id}).")

        # ----------------------------------------------------
        # 5. Assign Current User (Admin) to the Admin Group
        # ----------------------------------------------------
        print("\n--- Assigning Current User to Administrador Group ---")
        models.execute_kw(db, uid, password, 'res.users', 'write', [
            [uid], {
                'group_ids': [[4, admin_group_id]] # Add group to user's group_ids relation
            }
        ])
        print(f"  User ID {uid} added to group 'Amazon Ads / Administrador'.")

        # ----------------------------------------------------
        # 6. Initialize default Rules Record
        # ----------------------------------------------------
        print("\n--- Initializing default Rules in Odoo ---")
        existing_rules = models.execute_kw(db, uid, password, 'x_amazon_ads_rules', 'search', [[]])
        if not existing_rules:
            rule_vals = {
                'x_target_acos': 0.30,
                'x_max_spend_no_sales': 300.00,
                'x_min_clicks_no_sales': 10,
                'x_smoothing_factor': 0.3,
                'x_min_bid': 0.50,
                'x_max_bid': 100.00,
                'x_budget_transfer_pct': 0.15
            }
            r_id = models.execute_kw(db, uid, password, 'x_amazon_ads_rules', 'create', [rule_vals])
            print(f"  Inserted default Rules config record (ID: {r_id}).")
        else:
            print("  Rules configuration already exists.")

        print("\n=============================================")
        print("AMAZON ADS SECURITY GROUPS AND MENU COMPLETED")
        print("=============================================")

    except Exception as e:
        print(f"Error provisioning interface: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
