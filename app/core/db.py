import os
import json
import xmlrpc.client
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DBManager:
    def __init__(self):
        self.url = os.getenv("ODOO_URL")
        self.db = os.getenv("ODOO_DB")
        self.username = os.getenv("ODOO_USER")
        self.password = os.getenv("ODOO_API_KEY")
        self._uid = None
        self._models = None

    def get_connection(self):
        """Lazy-authenticates and returns XML-RPC connection parameters."""
        if self._uid and self._models:
            return self._uid, self._models
            
        if not all([self.url, self.db, self.username, self.password]):
            raise ValueError(f"Missing Odoo connection parameters in environment: URL={self.url}, DB={self.db}, User={self.username}")
            
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            uid = common.authenticate(self.db, self.username, self.password, {})
            if not uid:
                raise ValueError("Odoo XML-RPC authentication failed: invalid credentials.")
            
            self._uid = uid
            self._models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            return self._uid, self._models
        except Exception as err:
            raise ConnectionError(f"Failed to connect to Odoo XML-RPC server: {err}")

    # Credentials Management
    def save_credentials(self, client_id, client_secret, refresh_token, profile_id=None, region="na", mode="seller", test_mode=False):
        try:
            uid, models = self.get_connection()
            # Check if record exists
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_credentials', 'search', [
                [('x_mode', '=', mode)]
            ])
            
            vals = {
                'x_name': f"Perfil Amazon {mode.capitalize()}",
                'x_client_id': client_id,
                'x_client_secret': client_secret,
                'x_refresh_token': refresh_token,
                'x_profile_id': profile_id,
                'x_region': region,
                'x_mode': mode
            }
            
            if records:
                models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_credentials', 'write', [records, vals])
                print(f"[Odoo DB] Updated credentials for mode: {mode}")
            else:
                models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_credentials', 'create', [vals])
                print(f"[Odoo DB] Created credentials for mode: {mode}")
        except Exception as e:
            print(f"[Odoo DB] Error saving credentials: {e}")

    def get_credentials(self, mode="seller", test_mode=False):
        try:
            uid, models = self.get_connection()
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_credentials', 'search_read', [
                [('x_mode', '=', mode)]
            ], {'limit': 1})
            if records:
                rec = records[0]
                return {
                    "client_id": rec.get("x_client_id") or "",
                    "client_secret": rec.get("x_client_secret") or "",
                    "refresh_token": rec.get("x_refresh_token") or "",
                    "profile_id": rec.get("x_profile_id") or None,
                    "region": rec.get("x_region") or "na",
                    "mode": rec.get("x_mode") or mode,
                    "configured": True,
                    "updated_at": rec.get("write_date", datetime.utcnow().isoformat())
                }
        except Exception as e:
            print(f"[Odoo DB] Error fetching credentials for {mode}: {e}")
        
        # Fallback to env file
        env_client_id = os.getenv("LWA_CLIENT_ID")
        env_client_secret = os.getenv("LWA_CLIENT_SECRET")
        env_refresh_token = os.getenv("LWA_REFRESH_TOKEN")
        if env_client_id and env_client_secret and env_refresh_token and mode == "seller":
            return {
                "client_id": env_client_id,
                "client_secret": env_client_secret,
                "refresh_token": env_refresh_token,
                "profile_id": os.getenv("AMAZON_ADS_PROFILE_ID"),
                "region": os.getenv("AMAZON_ADS_REGION", "na"),
                "mode": "seller",
                "configured": True,
                "updated_at": datetime.utcnow().isoformat()
            }
        return {
            "client_id": "demo_client_id",
            "client_secret": "",
            "refresh_token": "",
            "profile_id": None,
            "region": "na",
            "mode": mode,
            "configured": False,
            "updated_at": datetime.utcnow().isoformat()
        }

    def update_profile_id(self, profile_id, mode="seller", test_mode=False):
        try:
            uid, models = self.get_connection()
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_credentials', 'search', [
                [('x_mode', '=', mode)]
            ])
            if records:
                models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_credentials', 'write', [records, {
                    'x_profile_id': profile_id
                }])
                print(f"[Odoo DB] Updated profile ID to {profile_id} for mode: {mode}")
        except Exception as e:
            print(f"[Odoo DB] Error updating profile ID: {e}")

    # Rules Management
    def get_rules(self, test_mode=False):
        try:
            uid, models = self.get_connection()
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_rules', 'search_read', [[]], {'limit': 1})
            if records:
                rec = records[0]
                return {
                    "id": rec.get("id"),
                    "target_acos": rec.get("x_target_acos") or 0.30,
                    "max_spend_no_sales": rec.get("x_max_spend_no_sales") or 300.0,
                    "min_clicks_no_sales": rec.get("x_min_clicks_no_sales") or 10,
                    "smoothing_factor": rec.get("x_smoothing_factor") or 0.3,
                    "min_bid": rec.get("x_min_bid") or 0.50,
                    "max_bid": rec.get("x_max_bid") or 100.0,
                    "budget_transfer_pct": rec.get("x_budget_transfer_pct") or 0.15,
                    "updated_at": rec.get("write_date", datetime.utcnow().isoformat())
                }
        except Exception as e:
            print(f"[Odoo DB] Error fetching optimization rules: {e}")
        
        # Fallback to default rule configuration
        return {
            "id": 1,
            "target_acos": 0.30,
            "max_spend_no_sales": 300.00,
            "min_clicks_no_sales": 10,
            "smoothing_factor": 0.3,
            "min_bid": 0.50,
            "max_bid": 100.00,
            "budget_transfer_pct": 0.15,
            "updated_at": datetime.utcnow().isoformat()
        }

    def update_rules(self, target_acos, max_spend, min_clicks, smoothing, min_bid, max_bid, budget_transfer, test_mode=False):
        try:
            uid, models = self.get_connection()
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_rules', 'search', [[]])
            
            vals = {
                'x_target_acos': target_acos,
                'x_max_spend_no_sales': max_spend,
                'x_min_clicks_no_sales': min_clicks,
                'x_smoothing_factor': smoothing,
                'x_min_bid': min_bid,
                'x_max_bid': max_bid,
                'x_budget_transfer_pct': budget_transfer
            }
            
            if records:
                models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_rules', 'write', [records, vals])
            else:
                models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_rules', 'create', [vals])
            return self.get_rules(test_mode=test_mode)
        except Exception as e:
            print(f"[Odoo DB] Error updating rules: {e}")
            return self.get_rules(test_mode=test_mode)

    # History Logging
    def log_optimization(self, opt_type, status, keywords_updated, negatives_created, budgets_redistributed, original_acos, new_acos_est, details, test_mode=False):
        try:
            uid, models = self.get_connection()
            vals = {
                'x_timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                'x_type': opt_type,
                'x_status': status,
                'x_keywords_updated': keywords_updated,
                'x_negatives_created': negatives_created,
                'x_budgets_redistributed': budgets_redistributed,
                'x_original_acos': original_acos,
                'x_new_acos_est': new_acos_est,
                'x_details_json': json.dumps(details)
            }
            models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_run_history', 'create', [vals])
            print(f"[Odoo DB] Optimization logged successfully ({opt_type})")
        except Exception as e:
            print(f"[Odoo DB] Error logging optimization history: {e}")

    def get_history(self, limit=50, test_mode=False):
        try:
            uid, models = self.get_connection()
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_run_history', 'search_read', [[]], {
                'limit': limit,
                'order': 'id desc'
            })
            history = []
            for r in records:
                details = {}
                if r.get("x_details_json"):
                    try:
                       details = json.loads(r["x_details_json"])
                    except Exception:
                       pass
                history.append({
                    "id": r["id"],
                    "timestamp": r.get("x_timestamp"),
                    "type": r.get("x_type"),
                    "status": r.get("x_status"),
                    "keywords_updated": r.get("x_keywords_updated") or 0,
                    "negatives_created": r.get("x_negatives_created") or 0,
                    "budgets_redistributed": r.get("x_budgets_redistributed") or 0,
                    "original_acos": r.get("x_original_acos") or 0.0,
                    "new_acos_est": r.get("x_new_acos_est") or 0.0,
                    "details": details
                })
            return history
        except Exception as e:
            print(f"[Odoo DB] Error fetching history: {e}")
            return []

    # Recommendations Cache
    def cache_suggestions(self, suggestions, test_mode=False):
        try:
            uid, models = self.get_connection()
            # Clear previous unapplied suggestions in Odoo
            unapplied_ids = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_suggestion', 'search', [
                [('x_applied', '=', False)]
            ])
            if unapplied_ids:
                models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_suggestion', 'unlink', [unapplied_ids])
                
            for sug in suggestions:
                vals = {
                    'x_source': sug.get("source") or "Unknown",
                    'x_entity_type': sug.get("entity_type") or "Keyword",
                    'x_campaign_name': sug.get("campaign_name") or "",
                    'x_ad_group_name': sug.get("ad_group_name") or "",
                    'x_keyword_text': sug.get("keyword_text") or "",
                    'x_match_type': sug.get("match_type") or "",
                    'x_current_value': float(sug.get("current_value") or 0.0),
                    'x_recommended_value': float(sug.get("recommended_value") or 0.0),
                    'x_recommendation_type': sug.get("recommendation_type") or "BID_ADJUSTMENT",
                    'x_reason': sug.get("reason") or "",
                    'x_applied': False,
                    'x_metrics_json': json.dumps(sug.get("metrics") or {})
                }
                models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_suggestion', 'create', [vals])
            print(f"[Odoo DB] Cached {len(suggestions)} suggestions successfully")
        except Exception as e:
            print(f"[Odoo DB] Error caching suggestions: {e}")

    def get_cached_suggestions(self, test_mode=False):
        try:
            uid, models = self.get_connection()
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_suggestion', 'search_read', [
                [('x_applied', '=', False)]
            ])
            suggestions = []
            for r in records:
                metrics = {}
                if r.get("x_metrics_json"):
                    try:
                        metrics = json.loads(r["x_metrics_json"])
                    except Exception:
                        pass
                suggestions.append({
                    "id": r["id"],
                    "source": r.get("x_source"),
                    "entity_type": r.get("x_entity_type"),
                    "campaign_name": r.get("x_campaign_name"),
                    "ad_group_name": r.get("x_ad_group_name"),
                    "keyword_text": r.get("x_keyword_text"),
                    "match_type": r.get("x_match_type"),
                    "current_value": r.get("x_current_value") or 0.0,
                    "recommended_value": r.get("x_recommended_value") or 0.0,
                    "recommendation_type": r.get("x_recommendation_type"),
                    "reason": r.get("x_reason"),
                    "applied": r.get("x_applied") or False,
                    "metrics": metrics
                })
            return suggestions
        except Exception as e:
            print(f"[Odoo DB] Error fetching suggestions: {e}")
            return []

    def apply_cached_suggestion(self, suggestion_id, test_mode=False):
        try:
            uid, models = self.get_connection()
            models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_suggestion', 'write', [
                [suggestion_id], {
                    'x_applied': True
                }
            ])
            print(f"[Odoo DB] Applied suggestion ID: {suggestion_id}")
        except Exception as e:
            print(f"[Odoo DB] Error applying suggestion: {e}")

    def clear_cache(self, test_mode=False):
        try:
            uid, models = self.get_connection()
            unapplied_ids = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_suggestion', 'search', [
                [('x_applied', '=', False)]
            ])
            if unapplied_ids:
                models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_suggestion', 'unlink', [unapplied_ids])
            print("[Odoo DB] Cleared cached suggestions")
        except Exception as e:
            print(f"[Odoo DB] Error clearing cache: {e}")

    # Campaigns Synchronization
    def write_campaigns(self, campaigns_list):
        try:
            uid, models = self.get_connection()
            for c in campaigns_list:
                campaign_id = c.get("campaign_id") or c.get("campaign_name")
                existing = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_campaign', 'search_read', [
                    ['|', ('x_campaign_id', '=', campaign_id), ('x_name', '=', c.get("campaign_name"))]
                ], {'limit': 1})
                
                spend = float(c.get("spend") if "spend" in c else (existing[0].get("x_spend") if existing else 0.0))
                sales = float(c.get("sales") if "sales" in c else (existing[0].get("x_sales") if existing else 0.0))
                clicks = int(c.get("clicks") if "clicks" in c else (existing[0].get("x_clicks") if existing else 0))
                orders = int(c.get("orders") if "orders" in c else (existing[0].get("x_orders") if existing else 0))
                impressions = int(c.get("impressions") if "impressions" in c else (existing[0].get("x_impressions") if existing else 0))
                acos = spend / sales if sales > 0 else 0.0
                roas = sales / spend if spend > 0 else 0.0
                cr = orders / clicks if clicks > 0 else 0.0

                vals = {
                    'x_campaign_id': campaign_id,
                    'x_name': c.get("campaign_name") or (existing[0].get("x_name") if existing else ""),
                    'x_ad_type': c.get("adType") or (existing[0].get("x_ad_type") if existing else "sp"),
                    'x_budget': float(c.get("budget") if "budget" in c else (existing[0].get("x_budget") if existing else 0.0)),
                    'x_spend': spend,
                    'x_sales': sales,
                    'x_orders': orders,
                    'x_clicks': clicks,
                    'x_impressions': impressions,
                    'x_acos': acos,
                    'x_roas': roas,
                    'x_cr': cr
                }
                if existing:
                    models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_campaign', 'write', [[existing[0]["id"]], vals])
                else:
                    models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_campaign', 'create', [vals])
            print(f"[Odoo DB] Synchronized {len(campaigns_list)} campaigns with Odoo")
        except Exception as e:
            print(f"[Odoo DB] Error writing campaigns to Odoo: {e}")

    def read_campaigns(self):
        try:
            uid, models = self.get_connection()
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_campaign', 'search_read', [[]])
            campaigns = []
            for r in records:
                campaigns.append({
                    "campaign_id": r.get("x_campaign_id") or str(r["id"]),
                    "campaign_name": r.get("x_name"),
                    "adType": r.get("x_ad_type") or "sp",
                    "budget": r.get("x_budget") or 0.0,
                    "spend": r.get("x_spend") or 0.0,
                    "sales": r.get("x_sales") or 0.0,
                    "orders": r.get("x_orders") or 0,
                    "clicks": r.get("x_clicks") or 0,
                    "impressions": r.get("x_impressions") or 0,
                    "acos": r.get("x_acos") or 0.0,
                    "roas": r.get("x_roas") or 0.0,
                    "cr": r.get("x_cr") or 0.0
                })
            return campaigns
        except Exception as e:
            print(f"[Odoo DB] Error reading campaigns from Odoo: {e}")
            return []

    # Products Performance Synchronization
    def write_products(self, products_list):
        try:
            uid, models = self.get_connection()
            for p in products_list:
                sku = p.get("sku")
                existing = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_product', 'search_read', [
                    [('x_sku', '=', sku)]
                ], {'limit': 1})
                
                # Try to find matching native Odoo product by reference
                odoo_product_id = False
                native_p = models.execute_kw(self.db, uid, self.password, 'product.product', 'search', [
                    [('default_code', '=', sku)]
                ], {'limit': 1})
                if native_p:
                    odoo_product_id = native_p[0]

                if existing:
                    rec = existing[0]
                    vals = {
                        'x_name': p.get("name") or rec.get("x_name") or "",
                        'x_asin': p.get("asin") or rec.get("x_asin") or "",
                        'x_category': p.get("category") or rec.get("x_category") or "",
                        'x_units_sold': int(p.get("units") if "units" in p else rec.get("x_units_sold") or 0),
                        'x_clicks': int(p.get("clicks") if "clicks" in p else rec.get("x_clicks") or 0),
                        'x_spend': float(p.get("spend") if "spend" in p else rec.get("x_spend") or 0.0),
                        'x_sponsored_sales': float(p.get("sales") if "sales" in p else rec.get("x_sponsored_sales") or 0.0),
                        'x_organic_sales': float(p.get("organic_sales") if "organic_sales" in p else rec.get("x_organic_sales") or 0.0),
                        'x_global_sales': float(p.get("global_sales") if "global_sales" in p else rec.get("x_global_sales") or 0.0),
                        'x_acos': float(p.get("acos") if "acos" in p else rec.get("x_acos") or 0.0),
                        'x_tacos': float(p.get("tacos") if "tacos" in p else rec.get("x_tacos") or 0.0),
                        'x_roas': float(p.get("roas") if "roas" in p else rec.get("x_roas") or 0.0),
                        'x_odoo_product_id': odoo_product_id
                    }
                    models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_product', 'write', [[rec["id"]], vals])
                else:
                    vals = {
                        'x_sku': sku,
                        'x_name': p.get("name") or "",
                        'x_asin': p.get("asin") or "",
                        'x_category': p.get("category") or "",
                        'x_units_sold': int(p.get("units") or 0),
                        'x_clicks': int(p.get("clicks") or 0),
                        'x_spend': float(p.get("spend") or 0.0),
                        'x_sponsored_sales': float(p.get("sales") or 0.0),
                        'x_organic_sales': float(p.get("organic_sales") or 0.0),
                        'x_global_sales': float(p.get("global_sales") or 0.0),
                        'x_acos': float(p.get("acos") or 0.0),
                        'x_tacos': float(p.get("tacos") or 0.0),
                        'x_roas': float(p.get("roas") or 0.0),
                        'x_odoo_product_id': odoo_product_id
                    }
                    models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_product', 'create', [vals])
            print(f"[Odoo DB] Synchronized {len(products_list)} products with Odoo")
        except Exception as e:
            print(f"[Odoo DB] Error writing products to Odoo: {e}")

    def read_products(self):
        try:
            uid, models = self.get_connection()
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_product', 'search_read', [[]])
            products = []
            for r in records:
                products.append({
                    "sku": r.get("x_sku"),
                    "name": r.get("x_name"),
                    "asin": r.get("x_asin"),
                    "category": r.get("x_category"),
                    "units": r.get("x_units_sold") or 0,
                    "clicks": r.get("x_clicks") or 0,
                    "spend": r.get("x_spend") or 0.0,
                    "sales": r.get("x_sponsored_sales") or 0.0,
                    "organic_sales": r.get("x_organic_sales") or 0.0,
                    "global_sales": r.get("x_global_sales") or 0.0,
                    "acos": r.get("x_acos") or 0.0,
                    "tacos": r.get("x_tacos") or 0.0,
                    "roas": r.get("x_roas") or 0.0
                })
            return products
        except Exception as e:
            print(f"[Odoo DB] Error reading products from Odoo: {e}")
            return []

    # Books (Kindle KDP) Synchronization
    def write_books(self, books_list):
        try:
            uid, models = self.get_connection()
            for b in books_list:
                asin = b.get("asin")
                existing = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_book', 'search_read', [
                    [('x_asin', '=', asin)]
                ], {'limit': 1})
                if existing:
                    rec = existing[0]
                    vals = {
                        'x_title': b.get("title") or rec.get("x_title") or "",
                        'x_format': b.get("format") or rec.get("x_format") or "",
                        'x_royalty_pct': float(b.get("royalty_pct") if "royalty_pct" in b else rec.get("x_royalty_pct") or 0.0),
                        'x_price': float(b.get("price") if "price" in b else rec.get("x_price") or 0.0),
                        'x_units_sold': int(b.get("units") if "units" in b else rec.get("x_units_sold") or 0),
                        'x_clicks': int(b.get("clicks") if "clicks" in b else rec.get("x_clicks") or 0),
                        'x_spend': float(b.get("spend") if "spend" in b else rec.get("x_spend") or 0.0),
                        'x_sponsored_sales': float(b.get("sales") if "sales" in b else rec.get("x_sponsored_sales") or 0.0),
                        'x_royalties_est': float(b.get("royalties") if "royalties" in b else rec.get("x_royalties_est") or 0.0),
                        'x_acos': float(b.get("acos") if "acos" in b else rec.get("x_acos") or 0.0),
                        'x_racos': float(b.get("racos") if "racos" in b else rec.get("x_racos") or 0.0),
                        'x_roas': float(b.get("roas") if "roas" in b else rec.get("x_roas") or 0.0),
                        'x_net_profit': float(b.get("net_profit") if "net_profit" in b else rec.get("x_net_profit") or 0.0)
                    }
                    models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_book', 'write', [[rec["id"]], vals])
                else:
                    vals = {
                        'x_asin': asin,
                        'x_title': b.get("title") or "",
                        'x_format': b.get("format") or "",
                        'x_royalty_pct': float(b.get("royalty_pct") or 0.0),
                        'x_price': float(b.get("price") or 0.0),
                        'x_units_sold': int(b.get("units") or 0),
                        'x_clicks': int(b.get("clicks") or 0),
                        'x_spend': float(b.get("spend") or 0.0),
                        'x_sponsored_sales': float(b.get("sales") or 0.0),
                        'x_royalties_est': float(b.get("royalties") or 0.0),
                        'x_acos': float(b.get("acos") or 0.0),
                        'x_racos': float(b.get("racos") or 0.0),
                        'x_roas': float(b.get("roas") or 0.0),
                        'x_net_profit': float(b.get("net_profit") or 0.0)
                    }
                    models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_book', 'create', [vals])
            print(f"[Odoo DB] Synchronized {len(books_list)} Kindle books with Odoo")
        except Exception as e:
            print(f"[Odoo DB] Error writing books to Odoo: {e}")

    def read_books(self):
        try:
            uid, models = self.get_connection()
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_book', 'search_read', [[]])
            books = []
            for r in records:
                books.append({
                    "asin": r.get("x_asin"),
                    "title": r.get("x_title"),
                    "format": r.get("x_format"),
                    "royalty_pct": r.get("x_royalty_pct") or 0.0,
                    "price": r.get("x_price") or 0.0,
                    "units": r.get("x_units_sold") or 0,
                    "clicks": r.get("x_clicks") or 0,
                    "spend": r.get("x_spend") or 0.0,
                    "sales": r.get("x_sponsored_sales") or 0.0,
                    "royalties": r.get("x_royalties_est") or 0.0,
                    "acos": r.get("x_acos") or 0.0,
                    "racos": r.get("x_racos") or 0.0,
                    "roas": r.get("x_roas") or 0.0,
                    "net_profit": r.get("x_net_profit") or 0.0
                })
            return books
        except Exception as e:
            print(f"[Odoo DB] Error reading books from Odoo: {e}")
            return []


    # Keywords Sync
    def write_keywords(self, keywords_list):
        try:
            uid, models = self.get_connection()
            # 1. Fetch campaigns map to resolve many2one IDs
            campaign_records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_campaign', 'search_read', [[]], {'fields': ['id', 'x_name']})
            campaign_map = {c['x_name']: c['id'] for c in campaign_records}
            
            # 2. Fetch existing keywords to check updates
            existing_kw_records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_keyword', 'search_read', [[]], {'fields': ['id', 'x_keyword_id']})
            existing_kw_map = {r['x_keyword_id']: r['id'] for r in existing_kw_records if r.get('x_keyword_id')}
            
            for kw in keywords_list:
                c_name = kw.get("campaign_name")
                campaign_db_id = campaign_map.get(c_name)
                if not campaign_db_id:
                    # Skip if campaign doesn't exist
                    continue
                    
                ad_group = kw.get("ad_group_name") or ""
                kw_text = kw.get("keyword_text") or ""
                match_type = kw.get("match_type") or ""
                keyword_id = kw.get("keyword_id") or f"{c_name} | {ad_group} | {kw_text} | {match_type}"
                
                vals = {
                    'x_keyword_id': keyword_id,
                    'x_campaign_id': campaign_db_id,
                    'x_ad_group_name': ad_group,
                    'x_keyword_text': kw_text,
                    'x_match_type': match_type,
                    'x_current_bid': float(kw.get("bid") or kw.get("current_value") or 0.0),
                    'x_clicks': int(kw.get("clicks") or 0),
                    'x_spend': float(kw.get("spend") or 0.0),
                    'x_sales': float(kw.get("sales") or 0.0),
                    'x_orders': int(kw.get("orders") or 0)
                }
                
                if keyword_id in existing_kw_map:
                    models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_keyword', 'write', [[existing_kw_map[keyword_id]], vals])
                else:
                    models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_keyword', 'create', [vals])
            print(f"[Odoo DB] Synchronized {len(keywords_list)} keywords with Odoo")
        except Exception as e:
            print(f"[Odoo DB] Error writing keywords to Odoo: {e}")

    def read_keywords(self):
        try:
            uid, models = self.get_connection()
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_keyword', 'search_read', [[]])
            keywords = []
            for r in records:
                camp_val = r.get("x_campaign_id")
                camp_name = camp_val[1] if isinstance(camp_val, list) else ""
                keywords.append({
                    "keyword_id": r.get("x_keyword_id"),
                    "campaign_name": camp_name,
                    "ad_group_name": r.get("x_ad_group_name") or "",
                    "keyword_text": r.get("x_keyword_text") or "",
                    "match_type": r.get("x_match_type") or "",
                    "bid": r.get("x_current_bid") or 0.0,
                    "clicks": r.get("x_clicks") or 0,
                    "spend": r.get("x_spend") or 0.0,
                    "sales": r.get("x_sales") or 0.0,
                    "orders": r.get("x_orders") or 0
                })
            return keywords
        except Exception as e:
            print(f"[Odoo DB] Error reading keywords from Odoo: {e}")
            return []

    # Search Terms Sync
    def write_search_terms(self, search_terms_list):
        try:
            uid, models = self.get_connection()
            # 1. Fetch campaigns map
            campaign_records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_campaign', 'search_read', [[]], {'fields': ['id', 'x_name']})
            campaign_map = {c['x_name']: c['id'] for c in campaign_records}
            
            # 2. Fetch existing search terms
            existing_st_records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_search_term', 'search_read', [[]], {'fields': ['id', 'x_campaign_id', 'x_ad_group_name', 'x_search_term']})
            existing_st_map = {}
            for r in existing_st_records:
                camp_id_val = r.get('x_campaign_id')
                camp_id = camp_id_val[0] if isinstance(camp_id_val, list) else camp_id_val
                existing_st_map[(camp_id, r.get('x_ad_group_name'), r.get('x_search_term'))] = r['id']
                
            for st in search_terms_list:
                c_name = st.get("campaign_name")
                campaign_db_id = campaign_map.get(c_name)
                if not campaign_db_id:
                    continue
                    
                ad_group = st.get("ad_group_name") or ""
                s_term = st.get("search_term") or st.get("customer_search_term") or ""
                
                vals = {
                    'x_campaign_id': campaign_db_id,
                    'x_ad_group_name': ad_group,
                    'x_search_term': s_term,
                    'x_clicks': int(st.get("clicks") or 0),
                    'x_spend': float(st.get("spend") or 0.0),
                    'x_sales': float(st.get("sales") or 0.0),
                    'x_orders': int(st.get("orders") or 0)
                }
                
                key = (campaign_db_id, ad_group, s_term)
                if key in existing_st_map:
                    models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_search_term', 'write', [[existing_st_map[key]], vals])
                else:
                    models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_search_term', 'create', [vals])
            print(f"[Odoo DB] Synchronized {len(search_terms_list)} search terms with Odoo")
        except Exception as e:
            print(f"[Odoo DB] Error writing search terms to Odoo: {e}")

    def read_search_terms(self):
        try:
            uid, models = self.get_connection()
            records = models.execute_kw(self.db, uid, self.password, 'x_amazon_ads_search_term', 'search_read', [[]])
            search_terms = []
            for r in records:
                camp_val = r.get("x_campaign_id")
                camp_name = camp_val[1] if isinstance(camp_val, list) else ""
                search_terms.append({
                    "campaign_name": camp_name,
                    "ad_group_name": r.get("x_ad_group_name") or "",
                    "customer_search_term": r.get("x_search_term") or "",
                    "search_term": r.get("x_search_term") or "",
                    "clicks": r.get("x_clicks") or 0,
                    "spend": r.get("x_spend") or 0.0,
                    "sales": r.get("x_sales") or 0.0,
                    "orders": r.get("x_orders") or 0
                })
            return search_terms
        except Exception as e:
            print(f"[Odoo DB] Error reading search terms from Odoo: {e}")
            return []

    # Odoo Discuss notifications
    def post_discuss_message(self, channel_name, subject, message_html):
        try:
            uid, models = self.get_connection()
            channel_ids = models.execute_kw(self.db, uid, self.password, 'discuss.channel', 'search', [
                [('name', '=', channel_name)]
            ])
            if channel_ids:
                channel_id = channel_ids[0]
            else:
                channel_id = models.execute_kw(self.db, uid, self.password, 'discuss.channel', 'create', [{
                    'name': channel_name,
                    'channel_type': 'channel',
                }])
            
            # Post the message
            models.execute_kw(self.db, uid, self.password, 'discuss.channel', 'message_post', [channel_id], {
                'body': f"<h4>{subject}</h4>{message_html}",
                'message_type': 'comment',
                'subtype_xmlid': 'mail.mt_comment'
            })
            print(f"[Odoo DB] Discuss message posted to '{channel_name}'")
            return True
        except Exception as e:
            print(f"[Odoo DB] Error posting discuss message: {e}")
            return False

# Single instance
db = DBManager()

