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

# Split into lines
def split_lines(tok):
    # We split by lengths: 121, 120, 121, 120, 44 or similar
    lines = []
    curr = tok
    for l in [121, 120, 121, 120, 44]:
        lines.append(curr[:l])
        curr = curr[l:]
    if curr:
        lines.append(curr)
    return lines

lines_384 = split_lines(t384)
lines_790 = split_lines(t790)

print("--- Token 384 ---")
for i, l in enumerate(lines_384):
    print(f"Line {i+1} (len {len(l)}): {l}")

print("\n--- Token 790 ---")
for i, l in enumerate(lines_790):
    print(f"Line {i+1} (len {len(l)}): {l}")
