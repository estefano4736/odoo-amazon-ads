import urllib.request
import urllib.parse
import json

client_id = "amzn1.application-oa2-client.ddb1420bb23444d8b7875824b97597c3"
client_secret = "amzn1.oa2-cs.v1.4e6260b40f624dd6eef59612836999321e893b05c9e173f84fc66ec26c379a51"

# Visually verified exact token:
token = (
    "Atzr|IwEBIK9J2ymp-IIa0gNJgCqnUogGnaPy8i-TZbGp1WsvkcjneE5IjsRplhwLlFke1FcCtsLKJVkCEsJfSQ0GhIugMvtivufhIs2Gy0Z8RtaunOb8hCyo"
    "tfYDoVrGCKBn0tuXLYMoTp3L8pUhyUbpY6YHRrNvyK-oiTJ7jNS8vwdDKRA2URxR02rCICbtzy6QqLKZMOEc29Qclrv72N2AbdY7Kp0vDFmP-DMDHxkBKlu6"
    "z0RAw6nzQ7I7ZXHGHgfdD1ABI-T42u3axtYzrbLw1UePHOoTJoMhfS_XejvziFv48qZhBt9p40q0Uzy6g_qd3Dh2IUWPZdWSPNuoGRVMsrZ-aqN3N9cqwwDDw"
    "z07A1TBQ3R0Ykhrfp0JnTMMUGxstP9qZ4R5reHP1AnLE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GYI1yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB"
    "NrhWLL9MkmMUP1UMFAf-cUBQoXthiIz9rUbUu7xw94bc"
)

def test_token(tok):
    url = "https://api.amazon.com/auth/o2/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": tok
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode("utf-8"))
            if "access_token" in res:
                return True, res
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        return False, err_msg
    except Exception as e:
        return False, str(e)

print(f"Testing visually reconstructed token of length {len(token)}...")
success, response = test_token(token)
if success:
    print("\n=========================================")
    print("✓ SUCCESS! Refresh Token is valid:")
    print(token)
    print("=========================================\n")
    print("API Response:", response)
else:
    print("\nFAILED:", response)
