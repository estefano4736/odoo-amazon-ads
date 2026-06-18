#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.parse

def exchange_code(client_id, client_secret, code, redirect_uri="http://127.0.0.1:8001/"):
    url = "https://api.amazon.com/auth/o2/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    # URL encode payload
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print("Enviando solicitud de intercambio de token a Amazon LWA...")
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print("\n======================================================================")
            print("✓ ¡ÉXITO! Conexión LWA de Amazon Ads Autorizada Correctamente")
            print("======================================================================")
            print(f"Refresh Token:\n\n{res_data.get('refresh_token')}\n")
            print("======================================================================")
            print("Instrucción:")
            print("1. Copia el 'Refresh Token' de arriba completo (empieza con Atzr|...).")
            print("2. Abre tu panel de control local en: http://127.0.0.1:8001")
            print("3. Haz clic en el ícono de engranaje (ajustes) arriba a la derecha.")
            print("4. Introduce tu Client ID, tu Client Secret, pega el Refresh Token y selecciona 'N. América'.")
            print("5. Haz clic en 'Guardar & Verificar Conexión'.")
            print("======================================================================\n")
    except urllib.error.HTTPError as e:
        print(f"\n✗ ERROR de respuesta de Amazon (Código {e.code}):")
        print(e.read().decode("utf-8"))
    except Exception as e:
        print(f"\n✗ ERROR inesperado al conectar: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python3 get_refresh_token.py <client_id> <client_secret> <code> [redirect_uri]")
        print("\nEjemplo:")
        print("  python3 get_refresh_token.py amzn1.application-oa2-client.123 789xyz Atzc|abc http://127.0.0.1:8001/")
        sys.exit(1)
        
    client_id = sys.argv[1]
    client_secret = sys.argv[2]
    code = sys.argv[3]
    redirect_uri = sys.argv[4] if len(sys.argv) > 4 else "http://127.0.0.1:8001/"
    exchange_code(client_id, client_secret, code, redirect_uri)
