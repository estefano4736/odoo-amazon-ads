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

        # Helper to create custom model
        def create_custom_model(model_name, label, info):
            existing = get_model_id(model_name)
            if existing:
                print(f"Model '{model_name}' already exists (ID: {existing}).")
                return existing
            
            vals = {
                'name': label,
                'model': model_name,
                'state': 'manual',
                'info': info
            }
            m_id = models.execute_kw(db, uid, password, 'ir.model', 'create', [vals])
            print(f"Created custom model '{model_name}' (ID: {m_id}).")
            return m_id

        # Helper to create custom field
        def create_custom_field(model_name, field_name, label, f_type, relation=None, selection=None, relation_field=None):
            model_id = get_model_id(model_name)
            if not model_id:
                print(f"Error: Model '{model_name}' not found.")
                return None
                
            # Check if field already exists
            existing = models.execute_kw(db, uid, password, 'ir.model.fields', 'search', [
                [('model_id', '=', model_id), ('name', '=', field_name)]
            ])
            if existing:
                print(f"  Field '{field_name}' already exists on '{model_name}'.")
                return existing[0]
                
            vals = {
                'model_id': model_id,
                'name': field_name,
                'field_description': label,
                'ttype': f_type,
                'state': 'manual',
            }
            if relation:
                vals['relation'] = relation
            if selection:
                vals['selection'] = str(selection)
            if relation_field:
                vals['relation_field'] = relation_field
                
            field_id = models.execute_kw(db, uid, password, 'ir.model.fields', 'create', [vals])
            print(f"  Created Field '{field_name}' ({label}) on '{model_name}' (ID: {field_id}).")
            return field_id

        # ----------------------------------------------------
        # 1. Model: x_amazon_ads_credentials
        # ----------------------------------------------------
        print("\n--- Setting up x_amazon_ads_credentials ---")
        create_custom_model('x_amazon_ads_credentials', 'Amazon Ads Credentials', 'Credenciales de acceso a la API de Amazon Ads')
        create_custom_field('x_amazon_ads_credentials', 'x_name', 'Nombre del Perfil', 'char')
        create_custom_field('x_amazon_ads_credentials', 'x_client_id', 'Client ID (LWA)', 'char')
        create_custom_field('x_amazon_ads_credentials', 'x_client_secret', 'Client Secret (LWA)', 'char')
        create_custom_field('x_amazon_ads_credentials', 'x_refresh_token', 'Refresh Token', 'char')
        create_custom_field('x_amazon_ads_credentials', 'x_profile_id', 'Profile ID', 'char')
        create_custom_field('x_amazon_ads_credentials', 'x_region', 'Región', 'selection', selection=[('na', 'North America'), ('eu', 'Europe'), ('fe', 'Far East')])
        create_custom_field('x_amazon_ads_credentials', 'x_mode', 'Modo', 'selection', selection=[('seller', 'Seller Central'), ('kindle', 'Kindle (KDP)')])

        # ----------------------------------------------------
        # 2. Model: x_amazon_ads_rules
        # ----------------------------------------------------
        print("\n--- Setting up x_amazon_ads_rules ---")
        create_custom_model('x_amazon_ads_rules', 'Amazon Ads Optimization Rules', 'Reglas y umbrales para el motor de optimización')
        create_custom_field('x_amazon_ads_rules', 'x_target_acos', 'Target ACOS', 'float')
        create_custom_field('x_amazon_ads_rules', 'x_max_spend_no_sales', 'Gasto Máximo Sin Ventas (MXN)', 'float')
        create_custom_field('x_amazon_ads_rules', 'x_min_clicks_no_sales', 'Mínimo Clics Sin Ventas', 'integer')
        create_custom_field('x_amazon_ads_rules', 'x_smoothing_factor', 'Factor de Suavizado (Bid Alpha)', 'float')
        create_custom_field('x_amazon_ads_rules', 'x_min_bid', 'Bid Mínimo', 'float')
        create_custom_field('x_amazon_ads_rules', 'x_max_bid', 'Bid Máximo', 'float')
        create_custom_field('x_amazon_ads_rules', 'x_budget_transfer_pct', 'Porcentaje Transferencia Presupuesto', 'float')

        # (Default rule insertion is moved to setup_odoo_interface.py after ACLs are created)

        # ----------------------------------------------------
        # 3. Model: x_amazon_ads_campaign
        # ----------------------------------------------------
        print("\n--- Setting up x_amazon_ads_campaign ---")
        create_custom_model('x_amazon_ads_campaign', 'Amazon Ads Campaign', 'Registro de campañas publicitarias de Amazon Ads')
        create_custom_field('x_amazon_ads_campaign', 'x_campaign_id', 'Campaign ID', 'char')
        create_custom_field('x_amazon_ads_campaign', 'x_name', 'Nombre de Campaña', 'char')
        create_custom_field('x_amazon_ads_campaign', 'x_ad_type', 'Tipo de Anuncio', 'selection', selection=[('sp', 'Sponsored Products'), ('sb', 'Sponsored Brands'), ('sd', 'Sponsored Display')])
        create_custom_field('x_amazon_ads_campaign', 'x_budget', 'Presupuesto Diario', 'float')
        create_custom_field('x_amazon_ads_campaign', 'x_spend', 'Gasto Publicitario', 'float')
        create_custom_field('x_amazon_ads_campaign', 'x_sales', 'Ventas Anuncios', 'float')
        create_custom_field('x_amazon_ads_campaign', 'x_orders', 'Pedidos', 'integer')
        create_custom_field('x_amazon_ads_campaign', 'x_clicks', 'Clics', 'integer')
        create_custom_field('x_amazon_ads_campaign', 'x_impressions', 'Impresiones', 'integer')
        create_custom_field('x_amazon_ads_campaign', 'x_acos', 'ACOS', 'float')
        create_custom_field('x_amazon_ads_campaign', 'x_roas', 'ROAS', 'float')
        create_custom_field('x_amazon_ads_campaign', 'x_cr', 'Tasa de Conversión (CR)', 'float')

        # ----------------------------------------------------
        # 4. Model: x_amazon_ads_keyword
        # ----------------------------------------------------
        print("\n--- Setting up x_amazon_ads_keyword ---")
        create_custom_model('x_amazon_ads_keyword', 'Amazon Ads Keyword Target', 'Palabras clave y targets publicitarios')
        create_custom_field('x_amazon_ads_keyword', 'x_keyword_id', 'Keyword ID', 'char')
        create_custom_field('x_amazon_ads_keyword', 'x_campaign_id', 'Campaña', 'many2one', relation='x_amazon_ads_campaign')
        create_custom_field('x_amazon_ads_keyword', 'x_ad_group_name', 'Grupo de Anuncios', 'char')
        create_custom_field('x_amazon_ads_keyword', 'x_keyword_text', 'Texto de Keyword', 'char')
        create_custom_field('x_amazon_ads_keyword', 'x_match_type', 'Coincidencia', 'char')
        create_custom_field('x_amazon_ads_keyword', 'x_current_bid', 'Bid Actual', 'float')
        create_custom_field('x_amazon_ads_keyword', 'x_clicks', 'Clics', 'integer')
        create_custom_field('x_amazon_ads_keyword', 'x_spend', 'Gasto', 'float')
        create_custom_field('x_amazon_ads_keyword', 'x_sales', 'Ventas', 'float')
        create_custom_field('x_amazon_ads_keyword', 'x_orders', 'Pedidos', 'integer')

        # Link from Campaign back to keywords
        create_custom_field('x_amazon_ads_campaign', 'x_keyword_ids', 'Keywords / Targets', 'one2many',
                            relation='x_amazon_ads_keyword', relation_field='x_campaign_id')

        # ----------------------------------------------------
        # 5. Model: x_amazon_ads_search_term
        # ----------------------------------------------------
        print("\n--- Setting up x_amazon_ads_search_term ---")
        create_custom_model('x_amazon_ads_search_term', 'Amazon Ads Search Term', 'Términos de búsqueda ingresados por clientes')
        create_custom_field('x_amazon_ads_search_term', 'x_campaign_id', 'Campaña', 'many2one', relation='x_amazon_ads_campaign')
        create_custom_field('x_amazon_ads_search_term', 'x_ad_group_name', 'Grupo de Anuncios', 'char')
        create_custom_field('x_amazon_ads_search_term', 'x_search_term', 'Término de Búsqueda', 'char')
        create_custom_field('x_amazon_ads_search_term', 'x_clicks', 'Clics', 'integer')
        create_custom_field('x_amazon_ads_search_term', 'x_spend', 'Gasto', 'float')
        create_custom_field('x_amazon_ads_search_term', 'x_sales', 'Ventas', 'float')
        create_custom_field('x_amazon_ads_search_term', 'x_orders', 'Pedidos', 'integer')

        # Link from Campaign back to search terms
        create_custom_field('x_amazon_ads_campaign', 'x_search_term_ids', 'Términos de Búsqueda', 'one2many',
                            relation='x_amazon_ads_search_term', relation_field='x_campaign_id')

        # ----------------------------------------------------
        # 6. Model: x_amazon_ads_product
        # ----------------------------------------------------
        print("\n--- Setting up x_amazon_ads_product ---")
        create_custom_model('x_amazon_ads_product', 'Amazon Ads Product Performance', 'Métricas de rendimiento por producto SKU de Amazon')
        create_custom_field('x_amazon_ads_product', 'x_sku', 'SKU del Producto', 'char')
        create_custom_field('x_amazon_ads_product', 'x_name', 'Nombre del Producto', 'char')
        create_custom_field('x_amazon_ads_product', 'x_asin', 'ASIN', 'char')
        create_custom_field('x_amazon_ads_product', 'x_category', 'Categoría', 'char')
        create_custom_field('x_amazon_ads_product', 'x_units_sold', 'Unidades Vendidas', 'integer')
        create_custom_field('x_amazon_ads_product', 'x_clicks', 'Clics', 'integer')
        create_custom_field('x_amazon_ads_product', 'x_spend', 'Gasto Ads', 'float')
        create_custom_field('x_amazon_ads_product', 'x_sponsored_sales', 'Ventas Publicidad', 'float')
        create_custom_field('x_amazon_ads_product', 'x_organic_sales', 'Ventas Orgánicas', 'float')
        create_custom_field('x_amazon_ads_product', 'x_global_sales', 'Ventas Globales', 'float')
        create_custom_field('x_amazon_ads_product', 'x_acos', 'ACOS', 'float')
        create_custom_field('x_amazon_ads_product', 'x_tacos', 'TACOS', 'float')
        create_custom_field('x_amazon_ads_product', 'x_roas', 'ROAS', 'float')
        # Link to native product if available
        create_custom_field('x_amazon_ads_product', 'x_odoo_product_id', 'Producto Odoo Nativo', 'many2one', relation='product.product')

        # ----------------------------------------------------
        # 7. Model: x_amazon_ads_book
        # ----------------------------------------------------
        print("\n--- Setting up x_amazon_ads_book ---")
        create_custom_model('x_amazon_ads_book', 'Amazon Ads KDP Book Performance', 'Métricas de regalías y libros Kindle KDP')
        create_custom_field('x_amazon_ads_book', 'x_asin', 'ASIN', 'char')
        create_custom_field('x_amazon_ads_book', 'x_title', 'Título del Libro', 'char')
        create_custom_field('x_amazon_ads_book', 'x_format', 'Formato', 'char')
        create_custom_field('x_amazon_ads_book', 'x_royalty_pct', 'Porcentaje Regalías', 'float')
        create_custom_field('x_amazon_ads_book', 'x_price', 'Precio', 'float')
        create_custom_field('x_amazon_ads_book', 'x_units_sold', 'Unidades Vendidas', 'integer')
        create_custom_field('x_amazon_ads_book', 'x_clicks', 'Clics', 'integer')
        create_custom_field('x_amazon_ads_book', 'x_spend', 'Gasto Ads', 'float')
        create_custom_field('x_amazon_ads_book', 'x_sponsored_sales', 'Ventas Anuncios', 'float')
        create_custom_field('x_amazon_ads_book', 'x_royalties_est', 'Regalías Estimadas', 'float')
        create_custom_field('x_amazon_ads_book', 'x_acos', 'ACOS Real', 'float')
        create_custom_field('x_amazon_ads_book', 'x_racos', 'RACoS (ACOS Regalías)', 'float')
        create_custom_field('x_amazon_ads_book', 'x_roas', 'ROAS', 'float')
        create_custom_field('x_amazon_ads_book', 'x_net_profit', 'Ganancia Neta KDP', 'float')

        # ----------------------------------------------------
        # 8. Model: x_amazon_ads_suggestion
        # ----------------------------------------------------
        print("\n--- Setting up x_amazon_ads_suggestion ---")
        create_custom_model('x_amazon_ads_suggestion', 'Amazon Ads Optimization Suggestion', 'Recomendaciones y sugerencias de optimización')
        create_custom_field('x_amazon_ads_suggestion', 'x_source', 'Origen', 'char')
        create_custom_field('x_amazon_ads_suggestion', 'x_entity_type', 'Entidad', 'selection', selection=[('Keyword', 'Keyword'), ('Campaign', 'Campaign'), ('SearchTerm', 'SearchTerm')])
        create_custom_field('x_amazon_ads_suggestion', 'x_campaign_name', 'Nombre Campaña', 'char')
        create_custom_field('x_amazon_ads_suggestion', 'x_ad_group_name', 'Grupo de Anuncios', 'char')
        create_custom_field('x_amazon_ads_suggestion', 'x_keyword_text', 'Palabra Clave / Target', 'char')
        create_custom_field('x_amazon_ads_suggestion', 'x_match_type', 'Coincidencia', 'char')
        create_custom_field('x_amazon_ads_suggestion', 'x_current_value', 'Valor Actual', 'float')
        create_custom_field('x_amazon_ads_suggestion', 'x_recommended_value', 'Valor Recomendado', 'float')
        create_custom_field('x_amazon_ads_suggestion', 'x_recommendation_type', 'Tipo de Optimización', 'selection', selection=[
            ('BID_ADJUSTMENT', 'Ajuste de Pujas (Bids)'),
            ('NEGATIVIZATION', 'Negativización de Términos'),
            ('BUDGET_REDISTRIBUTION', 'Redistribución de Presupuesto'),
            ('KEYWORD_HARVESTING', 'Cosecha de Palabras Clave (Harvesting)')
        ])
        create_custom_field('x_amazon_ads_suggestion', 'x_reason', 'Razón / Criterio', 'text')
        create_custom_field('x_amazon_ads_suggestion', 'x_applied', 'Aplicado', 'boolean')
        # Metrics cache JSON representation
        create_custom_field('x_amazon_ads_suggestion', 'x_metrics_json', 'Métricas JSON', 'text')

        # ----------------------------------------------------
        # 9. Model: x_amazon_ads_run_history
        # ----------------------------------------------------
        print("\n--- Setting up x_amazon_ads_run_history ---")
        create_custom_model('x_amazon_ads_run_history', 'Amazon Ads Optimization Run History', 'Bitácora de ejecuciones de optimización')
        create_custom_field('x_amazon_ads_run_history', 'x_timestamp', 'Fecha Ejecución', 'datetime')
        create_custom_field('x_amazon_ads_run_history', 'x_type', 'Tipo Ejecución', 'char')
        create_custom_field('x_amazon_ads_run_history', 'x_status', 'Estatus', 'char')
        create_custom_field('x_amazon_ads_run_history', 'x_keywords_updated', 'Palabras Actualizadas', 'integer')
        create_custom_field('x_amazon_ads_run_history', 'x_negatives_created', 'Negativos Creados', 'integer')
        create_custom_field('x_amazon_ads_run_history', 'x_budgets_redistributed', 'Redistribuciones Presupuesto', 'integer')
        create_custom_field('x_amazon_ads_run_history', 'x_original_acos', 'ACOS Inicial', 'float')
        create_custom_field('x_amazon_ads_run_history', 'x_new_acos_est', 'ACOS Proyectado', 'float')
        create_custom_field('x_amazon_ads_run_history', 'x_details_json', 'Detalles JSON', 'text')

        print("\n=============================================")
        print("AMAZON ADS DATABASE SCHEMAS CREATED IN ODOO")
        print("=============================================")

    except Exception as e:
        print(f"Error provisioning models: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
