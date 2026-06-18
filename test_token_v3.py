import urllib.request
import urllib.parse
import json

client_id = "amzn1.application-oa2-client.ddb1420bb23444d8b7875824b97597c3"
client_secret = "amzn1.oa2-cs.v1.4e6260b40f624dd6eef59612836999321e893b05c9e173f84fc66ec26c379a51"

# We noticed from the cropped image that:
# 1. "GCKBn0tu" is likely "GCKBnOtu" (capital O, since there is no dot inside).
# 2. "LlFke" is correct (lowercase l instead of 1).
# Let's define the base parts again:

part1_options = [
    # Option A: GCKBnOtu (capital O)
    "Atzr|IwEBIK9J2ymp-IIaOgNJgCqnUogGnaPy8i-TZbGp1WsvkcjneE5IjsRplhwLlFke1FcCtsLKJVkCEsJfSQ0GhIugMvtivufhIs2Gy0Z8RtaunOb8hCyotfYDoVrGCKBnOtuXLYMoTp3L8pUhyUbpY6YHRrNvyK-oiTJ7jNS8vwdDKRA2URxR02rCICbtzy6QqLKZMOEc29Qclrv72N2AbdY7Kp0vDFmP-DMDHxkBKIu6",
    # Option B: GCKBn0tu (number 0)
    "Atzr|IwEBIK9J2ymp-IIaOgNJgCqnUogGnaPy8i-TZbGp1WsvkcjneE5IjsRplhwLlFke1FcCtsLKJVkCEsJfSQ0GhIugMvtivufhIs2Gy0Z8RtaunOb8hCyotfYDoVrGCKBn0tuXLYMoTp3L8pUhyUbpY6YHRrNvyK-oiTJ7jNS8vwdDKRA2URxR02rCICbtzy6QqLKZMOEc29Qclrv72N2AbdY7Kp0vDFmP-DMDHxkBKIu6"
]

part2_options = [
    "z0RAW6nzQ7I7ZXHGHgfD1ABI-T42u3axtyzrbLw1UePHOoTJoMhfs_XejvziFv48qZhBt9p40qOUzy6g_qd3Dh2IUWPZdWSPNuoGRVMsrZ-aqN3N9cqwwDDw",
    "zORAW6nzQ7I7ZXHGHgfD1ABI-T42u3axtyzrbLw1UePHOoTJoMhfs_XejvziFv48qZhBt9p40qOUzy6g_qd3Dh2IUWPZdWSPNuoGRVMsrZ-aqN3N9cqwwDDw"
]

part3_options = [
    "z07A1TBQ3R0YkhrfpOJnTMMUGxstP9qZ4R5reHPlAnLE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GYI1yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB",
    "zO7A1TBQ3R0YkhrfpOJnTMMUGxstP9qZ4R5reHPlAnLE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GYI1yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB"
]

part4_options = [
    "NrhWLL9MkmMUP1UMFAf-cUBQoXthiIz9rUbUu7xw94bc",
    "NrhWLL9MkmMUP1UMFAf-cUBQoXthiIz9rUbUu7xw94bc".replace("Iz9r", "iz9r"),
    "NrhWLL9MkmMUP1UMFAf-cUBQoXthiIz9rUbUu7xw94bc".replace("Iz9r", "1z9r")
]

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

print("Testing permutations...")
found = False
for p1 in part1_options:
    for p2 in part2_options:
        for p3 in part3_options:
            for p4 in part4_options:
                candidate = p1 + p2 + p3 + p4
                success, res = test_token(candidate)
                if success:
                    print("\n=========================================")
                    print("SUCCESS! Valid token found:")
                    print(candidate)
                    print("=========================================\n")
                    found = True
                    break
            if found:
                break
        if found:
            break
    if found:
        break

if not found:
    print("None of the tested combinations succeeded.")
