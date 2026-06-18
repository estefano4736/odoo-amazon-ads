import urllib.request
import urllib.parse
import json
import asyncio
import http.client

client_id = "amzn1.application-oa2-client.ddb1420bb23444d8b7875824b97597c3"
client_secret = "amzn1.oa2-cs.v1.4e6260b40f624dd6eef59612836999321e893b05c9e173f84fc66ec26c379a51"

# We are confident about:
# IIa0g (with zero), LlFke, GCKBnOtu (with O), DMDHxk (capital H), HP1An (with 1), clrv72, GYI1, MUP1, Iz9r.

# Let's generate combinations for the remaining ambiguous ones:
# 1. BKIu6 vs BKlu6
# 2. Q7I7ZX vs Q7l7ZX
# 3. D1ABI vs DlABI vs D1ABl
# 4. Lw1Ue vs LwlUe
# 5. z07A1 vs z07Al

base_part1 = "Atzr|IwEBIK9J2ymp-IIa0gNJgCqnUogGnaPy8i-TZbGp1WsvkcjneE5IjsRplhwLlFke1FcCtsLKJVkCEsJfSQ0GhIugMvtivufhIs2Gy0Z8RtaunOb8hCyotfYDoVrGCKBnOtuXLYMoTp3L8pUhyUbpY6YHRrNvyK-oiTJ7jNS8vwdDKRA2URxR02rCICbtzy6QqLKZMOEc29Qclrv72N2AbdY7Kp0vDFmP-DMDHxk"
# Next is BK[I/l]u6
# Then part 2: z0RAW6nzQ7[I/l]7ZXHGHgf[D1ABI/DlABI/D1ABl]-T42u3axtyzrb[Lw1Ue/LwlUe]PHOoTJo...
# Then part 3: z07A[1/l]TBQ3R0YkhrfpOJnTMMUGxstP9qZ4R5reHP1AnLE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GYI1yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB
# Then part 4: NrhWLL9MkmMUP1UMFAf-cUBQoXthiIz9rUbUu7xw94bc

def get_candidates():
    candidates = []
    for bki in ["BKIu6", "BKlu6"]:
        p1 = base_part1 + bki
        for q7 in ["Q7I7ZX", "Q7l7ZX"]:
            for d1 in ["D1ABI", "DlABI", "D1ABl"]:
                for lw in ["Lw1Ue", "LwlUe"]:
                    p2 = f"z0RAW6nz{q7}HGHgf{d1}-T42u3axtyzrb{lw}PHOoTJoMhfs_XejvziFv48qZhBt9p40qOUzy6g_qd3Dh2IUWPZdWSPNuoGRVMsrZ-aqN3N9cqwwDDw"
                    for z07 in ["z07A1", "z07Al"]:
                        p3 = f"{z07}TBQ3R0YkhrfpOJnTMMUGxstP9qZ4R5reHP1AnLE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GYI1yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB"
                        p4 = "NrhWLL9MkmMUP1UMFAf-cUBQoXthiIz9rUbUu7xw94bc"
                        candidates.append(p1 + p2 + p3 + p4)
    return candidates

async def test_token_async(session, token):
    url = "https://api.amazon.com/auth/o2/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": token
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    
    # We use a custom runner using asyncio to avoid external library dependencies
    # since we want it to run out of the box in the .venv.
    loop = asyncio.get_event_loop()
    def make_req():
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode("utf-8"))
                if "access_token" in res:
                    return True, token
        except Exception as e:
            pass
        return False, None

    return await loop.run_in_executor(None, make_req)

async def main():
    candidates = get_candidates()
    print(f"Generated {len(candidates)} candidates. Testing asynchronously...")
    
    # Run in batches of 15 to avoid rate limiting or connection pool issues
    batch_size = 15
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        tasks = [test_token_async(None, cand) for cand in batch]
        results = await asyncio.gather(*tasks)
        for success, token in results:
            if success:
                print("\n=========================================")
                print("✓ SUCCESS! Valid token found:")
                print(token)
                print("=========================================\n")
                return
        print(f"Completed batch {i//batch_size + 1}/{len(candidates)//batch_size + 1}")
        await asyncio.sleep(0.5) # small delay between batches

    print("None of the combinations succeeded.")

if __name__ == "__main__":
    asyncio.run(main())
