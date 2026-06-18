import urllib.request
import urllib.parse
import json

client_id = "amzn1.application-oa2-client.ddb1420bb23444d8b7875824b97597c3"
client_secret = "amzn1.oa2-cs.v1.4e6260b40f624dd6eef59612836999321e893b05c9e173f84fc66ec26c379a51"

part1 = "Atzr|IwEBIK9J2ymp-IIaOgNJgCqnUogGnaPy8i-TZbGp1WsvkcjneE5IjsRplhwL1Fke1FcCtsLKJVkCEsJfSQ0GhIugMvtivufhIs2Gy0Z8RtaunOb8hCyotfYDoVrGCKBn0tuXLYMoTp3L8pUhyUbpY6YHRrNvyK-oiTJ7jNS8vwdDKRA2URxR02rCICbtzy6QqLKZMOEc29Qclrv72N2AbdY7Kp0vDFmP-DMDHxkBKIu6"
part2_options = [
    "z0RAW6nzQ7I7ZXHGHgfD1ABI-T42u3axtyzrbLw1UePHOoTJoMhfs_XejvziFv48qZhBt9p40qOUzy6g_qd3Dh2IUWPZdWSPNuoGRVMsrZ-aqN3N9cqwwDDw",
    "zORAW6nzQ7I7ZXHGHgfD1ABI-T42u3axtyzrbLw1UePHOoTJoMhfs_XejvziFv48qZhBt9p40qOUzy6g_qd3Dh2IUWPZdWSPNuoGRVMsrZ-aqN3N9cqwwDDw"
]
part3_options = [
    "z07A1TBQ3R0YkhrfpOJnTMMUGxstP9qZ4R5reHP1AnLE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GYI1yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB",
    "zO7A1TBQ3R0YkhrfpOJnTMMUGxstP9qZ4R5reHP1AnLE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GYI1yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB"
]
part4 = "NrhWLL9MkmMUP1UMFAf-cUBQoXthiIz9rUbUu7xw94bc"

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
    except Exception as e:
        pass
    return False, None

print("Testing token variations...")
found = False
for p2 in part2_options:
    for p3 in part3_options:
        candidate = part1 + p2 + p3 + part4
        success, response = test_token(candidate)
        if success:
            print("\nFOUND SUCCESSFUL TOKEN!")
            print(candidate)
            found = True
            break
    if found:
        break

if not found:
    print("None of the variations succeeded. Let's inspect the original code output.")
