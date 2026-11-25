from __future__ import annotations
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IS_T4_7 = [0 < m < 128 and m.bit_count() <= 4 for m in range(128)]
T7_W4 = sum(1 << m for m in range(128) if IS_T4_7[m])
IS_T4_6 = [0 < m < 64 and m.bit_count() <= 4 for m in range(64)]
T6_W4 = sum(1 << m for m in range(64) if IS_T4_6[m])

def req(ok):
    if not ok: raise AssertionError()

def seen(w):
    ps, cur, sm = [0], 0, 0
    for x in w[:-1]:
        cur ^= 1 << x
        for p in ps: sm |= 1 << (cur ^ p)
        ps.append(cur)
    return sm

def enum_dbl(n, k):
    out = []
    def dfs(p, w, c, nl):
        if p == n: out.append(w[:]); return
        for l in range(nl):
            if c[l] < 2: c[l] += 1; w.append(l); dfs(p+1, w, c, nl); w.pop(); c[l] -= 1
        if nl <= k: c[nl] += 1; w.append(nl); dfs(p+1, w, c, nl+1); w.pop(); c[nl] -= 1
    dfs(0, [], [0]*(k+1), 0)
    return out

all12 = enum_dbl(12, 5)
w12_cov = [(seen(w) & T6_W4).bit_count() for w in all12]
req(len(all12) == 10395 and max(w12_cov) == 48 and w12_cov.count(48) == 2)

all14 = enum_dbl(14, 6)
w14_cov = [(seen(w) & T7_W4).bit_count() for w in all14]
req(len(all14) == 135135 and max(w14_cov) == 70 and w14_cov.count(70) == 2)

w16_witness = [0, 1, 2, 0, 3, 1, 4, 3, 0, 5, 4, 0, 6, 5, 2, 6]
req((seen(w16_witness) & T7_W4).bit_count() == 79)

w18_62_witness = [0, 1, 0, 2, 3, 0, 1, 0, 4, 3, 5, 0, 4, 0, 6, 5, 2, 6]
req((seen(w18_62_witness) & T7_W4).bit_count() == 85)

w18_44_witness = [0, 1, 0, 2, 6, 3, 1, 6, 0, 4, 3, 0, 6, 5, 4, 6, 2, 5]
req((seen(w18_44_witness) & T7_W4).bit_count() == 91)

print("PASS_SEVEN_SOURCE_WEIGHT4_CONNECTOR_BOUNDARY L14_max=70/98 L16_max=79/98 L18_62_max=85/98 L18_44_max=91/98 floor=216_calls")
