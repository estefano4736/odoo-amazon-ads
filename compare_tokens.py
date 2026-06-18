t384 = (
    "Atzr|IwEBIK9J2ymp-IIaOgNJgCqnUogGnaPy8i-TZbGp1WsvkcjneE5IjsRplhwL1Fke1FcCtsLKJVkCEsJfSQ0GhIugMvtivufhIs2Gy0Z8RtaunOb8hCyo"
    "tfYDoVrGCKBn0tuXLYMoTp3L8pUhyUbpY6YHRrNvyK-oiTJ7jNS8vwdDKRA2URxR02rCICbtzy6QqLKZMOEc29Qclrv72N2AbdY7Kp0vDFmP-DMDHxkBKIu6"
    "z0RAW6nzQ7I7ZXHGHgfD1ABI-T42u3axtyzrbLw1UePHOoTJoMhfs_XejvziFv48qZhBt9p40qOUzy6g_qd3Dh2IUWPZdWSPNuoGRVMsrZ-aqN3N9cqwwDDw"
    "z07A1TBQ3R0YkhrfpOJnTMMUGxstP9qZ4R5reHP1AnLE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GYI1yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB"
    "NrhWLL9MkmMUP1UMFAf-cUBQoXthiIz9rUbUu7xw94bc"
)

t790 = (
    "Atzr|IwEBIK9J2ymp-IIa0gNJgCqnUogGnaPy8i-TZbGp1WsvkcjneE5IjsRplhwLlFke1FcCtsLKJVkCEsJfSQ0GhIugMvtivufhIs2Gy0Z8RtaunOb8hCyo"
    "tfYDoVrGCKBn0tuXLYMoTp3L8pUhyUbpY6YHRrNvyK-oiTJ7jNS8vwdDKRA2URxR02rCICbtzy6QqLKZMOEc29Qclrv72N2AbdY7Kp0vDFmP-DMDHxkBKlu6"
    "z0RAw6nzQ7I7ZXHGHgfdD1ABI-T42u3axtYzrbLw1UePHOoTJoMhfS_XejvziFv48qZhBt9p40q0Uzy6g_qd3Dh2IUWPZdWSPNuoGRVMsrZ-aqN3N9cqwwDDw"
    "z07A1TBQ3R0Ykhrfp0JnTMMUGxstP9qZ4R5reHP1AnLE5sMfPMZmZTUREkyG7Sy_CGmHhoM5s7AFgJWoge6GYI1yXEOCayt7xbH7neL5UBAtbi8T4yEhfEXB"
    "NrhWLL9MkmMUP1UMFAf-cUBQoXthiIz9rUbUu7xw94bc"
)

print(f"Length 384: {len(t384)}")
print(f"Length 790: {len(t790)}")

import difflib
diff = list(difflib.ndiff(t384, t790))
for idx, char in enumerate(diff):
    if char.startswith('-') or char.startswith('+'):
        print(f"Diff at index context around {idx}: {''.join(diff[max(0, idx-10):idx+10])}")
