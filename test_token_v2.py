import urllib.request
import urllib.parse
import json

client_id = "amzn1.application-oa2-client.ddb1420bb23444d8b7875824b97597c3"
client_secret = "amzn1.oa2-cs.v1.4e6260b40f624dd6eef59612836999321e893b05c9e173f84fc66ec26c379a51"

# The token as transcribed from the screenshot:
# Line 1: Atzr|IwEBIK9J2ymp-IIaOgNJgCqnUogGnaPy8i-TZbGp1WsvkcjneE5IjsRplhwLlFke1FcCtsLKJVkCEsJfSQ0GhIugMvtivufhIs2Gy0Z8RtaunOb8hCyo
# Line 2: tfYDoVrGCKBn0tuXLYMoTp3L8pUhyUbpY6YHRrNvyK-oiTJ7jNS8vwdDKRA2URxR02rCICbtzy6QqLKZMOEc29Qclrv72N2AbdY7Kp0vDFmP-DMDHxkBKIu6
# Line 3: z0RAW6nzQ7I7ZXHGHgfD1ABI-T42u3axtyzrbLw1UePHOoTJoMhfs_XejvziFv48qZhBt9p40qOUzy6g_qd3Dh2IUWPZdWSPNuoGRVMsrZ-aqN3N9cqwwDDw
# Line 4: z07A1TBQ3R0YkhrfpOJnTMMUGxstP9qZ4R5reHPlAnLE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GYI1yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB
# Line 5: NrhWLL9MkmMUP1UMFAf-cUBQoXthiIz9rUbUu7xw94bc

# Let's define the base parts based on the screenshot:
part1_base = "Atzr|IwEBIK9J2ymp-IIaOgNJgCqnUogGnaPy8i-TZbGp1WsvkcjneE5IjsRplhwLlFke1FcCtsLKJVkCEsJfSQ0GhIugMvtivufhIs2Gy0Z8RtaunOb8hCyotfYDoVrGCKBn0tuXLYMoTp3L8pUhyUbpY6YHRrNvyK-oiTJ7jNS8vwdDKRA2URxR02rCICbtzy6QqLKZMOEc29Qclrv72N2AbdY7Kp0vDFmP-DMDHxkBKIu6"
part2_base = "z0RAW6nzQ7I7ZXHGHgfD1ABI-T42u3axtyzrbLw1UePHOoTJoMhfs_XejvziFv48qZhBt9p40qOUzy6g_qd3Dh2IUWPZdWSPNuoGRVMsrZ-aqN3N9cqwwDDw"
part3_base = "z07A1TBQ3R0YkhrfpOJnTMMUGxstP9qZ4R5reHPlAnLE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GYI1yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB"
part4_base = "NrhWLL9MkmMUP1UMFAf-cUBQoXthiIz9rUbUu7xw94bc"

def test_token(token):
    url = "https://api.amazon.com/auth/o2/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": token
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            if "access_token" in res:
                return True, res
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        return False, err_msg
    except Exception as e:
        return False, str(e)

# 1. Test the base token from screenshot
base_token = part1_base + part2_base + part3_base + part4_base
print("Testing base token...")
success, res = test_token(base_token)
if success:
    print("SUCCESS!", res)
else:
    print("Failed base token:", res)
