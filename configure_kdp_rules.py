import sqlite3
import os
from datetime import datetime

DATABASE_PATH = "./data/aaoe.db"

def configure_kdp_rules():
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: No se encontró la base de datos en '{DATABASE_PATH}'. Por favor, inicia el servidor primero con 'python run.py' para inicializarla.")
        return

    print("Conectando a la base de datos...")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # KDP-optimized values
    target_acos = 0.50            # 50% ACOS objetivo (apropiado para regalías del 70%)
    max_spend_no_sales = 30.00    # ~$1.50 USD de gasto máximo sin ventas (aprox. la mitad de una regalía estándar de libro de $4.99)
    min_clicks_no_sales = 12      # 12 clics sin conversión (CR del ~8% esperada)
    smoothing_factor = 0.3        # Modificación gradual de pujas
    min_bid = 0.02                # Puja mínima permitida por KDP/Amazon Ads
    max_bid = 0.35                # Puja máxima para evitar gastar toda la regalía en pocos clics
    budget_transfer_pct = 0.15    # Transferencia de presupuesto del 15%
    updated_at = datetime.utcnow().isoformat()

    try:
        # Check if record exists
        cursor.execute("SELECT COUNT(*) FROM rules WHERE id = 1")
        exists = cursor.fetchone()[0] > 0

        if exists:
            cursor.execute("""
                UPDATE rules SET 
                    target_acos = ?, 
                    max_spend_no_sales = ?, 
                    min_clicks_no_sales = ?, 
                    smoothing_factor = ?, 
                    min_bid = ?, 
                    max_bid = ?, 
                    budget_transfer_pct = ?, 
                    updated_at = ?
                WHERE id = 1
            """, (target_acos, max_spend_no_sales, min_clicks_no_sales, smoothing_factor, min_bid, max_bid, budget_transfer_pct, updated_at))
            print("✓ Reglas existentes actualizadas con configuraciones optimizadas para KDP.")
        else:
            cursor.execute("""
                INSERT INTO rules (id, target_acos, max_spend_no_sales, min_clicks_no_sales, smoothing_factor, min_bid, max_bid, budget_transfer_pct, updated_at)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (target_acos, max_spend_no_sales, min_clicks_no_sales, smoothing_factor, min_bid, max_bid, budget_transfer_pct, updated_at))
            print("✓ Nuevas reglas creadas y optimizadas para KDP.")

        conn.commit()
        
        # Verify the rules
        cursor.execute("SELECT * FROM rules WHERE id = 1")
        row = cursor.fetchone()
        print("\nConfiguración KDP Activa en Base de Datos:")
        print(f"  - ACOS Objetivo: {row[1]*100}%")
        print(f"  - Gasto Máximo sin Ventas: ${row[2]} MXN")
        print(f"  - Clics Mínimos sin Ventas: {row[3]}")
        print(f"  - Factor de Suavizado: {row[4]}")
        print(f"  - Puja Mínima: ${row[5]} MXN")
        print(f"  - Puja Máxima: ${row[6]} MXN")
        print(f"  - Transferencia de Presupuesto: {row[7]*100}%")

    except Exception as e:
        print(f"✗ Error al actualizar la base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    configure_kdp_rules()
