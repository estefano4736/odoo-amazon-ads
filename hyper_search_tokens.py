import asyncio
import urllib.request
import urllib.parse
import json
import os
import sys

# Set up path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import db

client_id = "amzn1.application-oa2-client.ddb1420bb23444d8b7875824b97597c3"
client_secret = "amzn1.oa2-cs.v1.4e6260b40f624dd6eef59612836999321e893b05c9e173f84fc66ec26c379a51"

def get_candidates():
    candidates = []
    
    # Define option arrays
    iiag_opts = ["IIa0g", "IIaOg"]
    lfk_opts = ["LlFke", "L1Fke", "LIFke"]
    gck_opts = ["GCKBn0tu", "GCKBnOtu"]
    yhr_opts = ["YHRr", "YHRRr"]
    bki_opts = ["BKlu6", "BKIu6", "BK1u6"]
    w_opts = ["w", "W"]
    q7_opts = ["Q7I7ZX", "Q7l7ZX"]
    d1_opts = ["dD1ABI", "dDlABI", "D1ABI", "DlABI"]
    s_opts = ["S", "s"]
    q0u_opts = ["q0Uzy", "qOUzy"]
    z07_opts = ["z07A1", "z07Al"]
    hp_opts = ["HP1An", "HPlAn"]
    gy_opts = ["GYI1", "GYIl"]
    mup_opts = ["MUP1", "MUPl"]
    
    print("Generating candidates for hyper search...")
    for iiag in iiag_opts:
        for lfk in lfk_opts:
            for gck in gck_opts:
                for yhr in yhr_opts:
                    for bki in bki_opts:
                        for w in w_opts:
                            for q7 in q7_opts:
                                for d1 in d1_opts:
                                    for s_char in s_opts:
                                        for q0u in q0u_opts:
                                            for z07 in z07_opts:
                                                for hp in hp_opts:
                                                    for gy in gy_opts:
                                                        for mup in mup_opts:
                                                            p1 = f"Atzr|IwEBIK9J2ymp-{iiag}NJgCqnUogGnaPy8i-TZbGp1WsvkcjneE5IjsRplhw{lfk}1FcCtsLKJVkCEsJfSQ0GhIugMvtivufhIs2Gy0Z8RtaunOb8hCyo"
                                                            p2 = f"tfYDoVr{gck}XLYMoTp3L8pUhyUbpY6{yhr}NvyK-oiTJ7jNS8vwdDKRA2URxR02rCICbtzy6QqLKZMOEc29Qclrv72N2AbdY7Kp0vDFmP-DMDHxk{bki}"
                                                            p3 = f"z0RA{w}6nz{q7}HGHgf{d1}-T42u3axtYzrbLw1UePHOoTJoMhf{s_char}_XejvziFv48qZhBt9p40{q0u}6g_qd3Dh2IUWPZdWSPNuoGRVMsrZ-aqN3N9cqwwDDw"
                                                            p4 = f"{z07}TBQ3R0Ykhrfp0JnTMMUGxstP9qZ4R5re{hp}LE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GY{gy}yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB"
                                                            p5 = f"NrhWLL9MkmMUP{mup[3]}UMFAf-cUBQoXthiIz9rUbUu7xw94bc"
                                                            candidates.append(p1 + p2 + p3 + p4 + p5)
                                                            
    return candidates

async def test_candidate(sem, cand, idx, total):
    url = "https://api.amazon.com/auth/o2/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": cand
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    
    async with sem:
        loop = asyncio.get_event_loop()
        def make_request():
            req = urllib.request.Request(
                url, 
                data=data, 
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            try:
                with urllib.request.urlopen(req, timeout=6) as response:
                    res_body = response.read().decode("utf-8")
                    res = json.loads(res_body)
                    if "access_token" in res:
                        return True, res
            except urllib.error.HTTPError as e:
                pass
            except Exception as e:
                pass
            return False, None

        success, res = await loop.run_in_executor(None, make_request)
        if success:
            return True, cand, res
        return False, None, None

async def main():
    candidates = get_candidates()
    total = len(candidates)
    print(f"Total candidates generated: {total}")
    
    # We will use 250 Semaphore concurrency for maximum throughput
    sem = asyncio.Semaphore(250)
    
    tasks = []
    for idx, cand in enumerate(candidates):
        tasks.append(test_candidate(sem, cand, idx, total))
        
    print("Testing 110,592 combinations asynchronously...")
    completed = 0
    chunk_size = 4000
    for i in range(0, total, chunk_size):
        chunk_tasks = tasks[i:i+chunk_size]
        results = await asyncio.gather(*chunk_tasks)
        completed += len(chunk_tasks)
        print(f"Tested {completed}/{total} ({completed/total*100:.1f}%) candidates...")
        
        for success, token, res in results:
            if success:
                print("\n======================================================================")
                print("✓ ¡ÉXITO! TOKEN VÁLIDO ENCONTRADO:")
                print(token)
                print("======================================================================")
                print("Respuesta API:", res)
                
                # Save to database
                print("Guardando credenciales válidas en la base de datos...")
                db.save_credentials(
                    client_id=client_id,
                    client_secret=client_secret,
                    refresh_token=token,
                    region="na"
                )
                print("✓ Credenciales guardadas y encriptadas correctamente en data/aaoe.db.")
                return
                
        await asyncio.sleep(0.02)
        
    print("Permutation search finished. No valid token found.")

if __name__ == "__main__":
    asyncio.run(main())
