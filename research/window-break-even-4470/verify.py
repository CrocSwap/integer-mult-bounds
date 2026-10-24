#!/usr/bin/env python3
"""Break-even line counts per dimension for short label windows under the #4470 invoice.

Standard library only. Rebuilds the joint-helper-lattice (#4470) complex invoice from its
local data, generalises it to a line system (v lines, rank T, window h, decoder cost D,
k deleted lines), and compares the lines-per-dimension needed to tie the record with the
Theorem B cap of research/line-system-saturation (v/T <= 2^k'+1 at odd window h = 2k'+1,
v/T <= 2^k' at even window h = 2k'). Writes and replays RESULT.json.
"""
import json
import math
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / 'research/joint-helper-lattice/RESULT.json'
BASE_PORTS, BASE_D = 112, 8


def bind():
    d = json.loads(SRC.read_text(encoding='utf-8'))
    H = {int(r): n for r, n in d['local_helpers'].items()}
    LP = {int(r): n for r, n in d['local_paid'].items()}
    centre = LP.pop(BASE_D)
    return dict(H=H, LP=LP, centre_jobs=centre, calls=d['full_calls'], pairs=d['pairs'],
                prefix=d['prefix_pairs'], shears=d['query_shears'],
                targets={int(r): n for r, n in d['targets'].items()},
                paid={int(r): n for r, n in d['paid'].items()},
                kappa=Q(d['kappa_decimal']))


def invoice(S, V, d, cjobs, crank, p, a, exact=False):
    """#4440 controller with p pairs (prefix a), local word scaled by V/112 (counts), d/8 (ranks)."""
    num = Q if exact else float
    n, s = num(V) / BASE_PORTS, num(d) / BASE_D
    T, P = Counter(), Counter()
    T[1 + d * (p + 2)] += 2 * V
    for j in list(range(1, a + 1)) + list(range(1, p - a)):
        T[1 + d * (j + 1)] += 2 * V
        P[d * (j + 1)] += 2 * V
    for r, m in S['H'].items():
        T[r * s] += (p + 2) * m * n
    for r, m in S['LP'].items():
        P[r * s] += (p + 2) * m * n
    P[crank] += (p + 2) * cjobs
    P[1] += V * (p - 1)
    return T, P


def root(T, P):
    """Positive root of sum_T r^(1-c) - sum_P r^(1-c); 0 if the surplus is not positive."""
    TT = [(math.log(r), m * r) for r, m in T.items() if m]
    PP = [(math.log(r), m * r) for r, m in P.items() if m]

    def f(c):
        return (sum(w * math.exp(-c * L) for L, w in TT) - sum(w * math.exp(-c * L) for L, w in PP),
                -sum(w * L * math.exp(-c * L) for L, w in TT) + sum(w * L * math.exp(-c * L) for L, w in PP))
    lo, hi = 0.0, 0.5
    if f(1e-13)[0] <= 0:
        return 0.0
    c = 0.003
    for _ in range(60):
        v, dv = f(c)
        if v > 0:
            lo = c
        else:
            hi = c
        nc = c - v / dv if dv < 0 else (lo + hi) / 2
        if not lo < nc < hi:
            nc = (lo + hi) / 2
        if abs(nc - c) < 1e-16:
            break
        c = nc
    return c


def best(S, v, T, h, D, k):
    V, d, c = v - k, h - 1, D - k
    out = (0.0, None, None)
    for p in range(3, 41):
        for a in range(1, p - 1):
            C = root(*invoice(S, V, d, T, c / T, p, a))
            if C > out[0]:
                out = (C, p, a)
    return out


def cap(h):
    kp = h // 2
    return 2 ** kp + 1 if h % 2 else 2 ** kp


SYSTEMS = [  # name, v, T, h, D, deleted lines k, source of (v, T, h, D)
    ('E8 P112 (selected #4470)', 120, 8, 9, 72, 8, 'char2-threshold G1.E8-gain; line-system-saturation c1'),
    ('E8 P111', 120, 8, 9, 72, 9, 'centre 63 (selected bit P111 analogue)'),
    ('E8 P104', 120, 8, 9, 72, 16, 'centre 56; complex P104 not built'),
    ('E7 roots', 63, 7, 7, 49, 7, 'char2-threshold G1.E7-gain'),
    ('E7 roots, two frames deleted', 63, 7, 7, 49, 14, 'same, k = 2T'),
    ('E6 roots', 36, 6, 7, 36, 6, 'char2-threshold G1.E6-tie'),
    ('D6 roots', 30, 6, 5, 30, 6, 'char2-threshold G1.D-ties'),
    ('D5 roots', 20, 5, 5, 20, 5, 'char2-threshold G1.D-ties'),
    ('D4 roots', 12, 4, 3, 12, 4, 'char2-threshold G1.D-ties'),
    ('Z8 (56 lines)', 56, 8, 7, 56, 8, 'line-system-saturation 8.1, dense'),
    ('E8+A3 (norms 6)', 140, 11, 11, 121, 11, 'line-system-saturation 8.1, dense'),
    ('D16+ roots + 256 spinors', 496, 16, 17, 272, 16, 'line-system-saturation 8.1, dense'),
    ('D16+ Delsarte cap 557', 557, 16, 17, 272, 16, 'line-system-saturation 8.2 upper bound'),
    ('D24+ roots + 176 spinors', 728, 24, 25, 600, 24, 'line-system-saturation 8.1, dense'),
]


def compute(S):
    rec = float(S['kappa'])
    out = {'record_rounded': str(S['kappa'])}
    # 1. exact reconstruction of #4470
    T0, P0 = invoice(S, BASE_PORTS, BASE_D, S['centre_jobs'], BASE_D, S['pairs'], S['prefix'], exact=True)
    assert {r: int(m) for r, m in T0.items() if m} == S['targets'], 'targets not reproduced'
    assert {r: int(m) for r, m in P0.items() if m} == S['paid'], 'paid not reproduced'
    c0 = root(*invoice(S, BASE_PORTS, BASE_D, S['centre_jobs'], BASE_D, S['pairs'], S['prefix']))
    assert S['kappa'] < Q(c0) < S['kappa'] + Q(1, 10**7), c0
    out['calibration_root'] = round(c0, 12)
    # 2. surplus identity S = (p+2)(v-D) - V on exact counts
    for (v, T, h, D, k) in [(120, 8, 9, 72, 8), (63, 7, 7, 49, 7), (63, 7, 7, 49, 14), (40, 4, 6, 24, 8)]:
        for p in (3, 9, 16, 30):
            Tp, Pp = invoice(S, v - k, h - 1, T, Q(D - k, T), p, p // 2, exact=True)
            surplus = sum(r * m for r, m in Tp.items()) - sum(r * m for r, m in Pp.items())
            assert surplus == (p + 2) * (v - D) - (v - k), (v, T, h, D, k, p)
    out['surplus_identity'] = 'S = (p+2)(v-D) - V, checked exactly on 16 instances'
    # 3. named systems
    rows = {}
    for name, v, T, h, D, k, src in SYSTEMS:
        C, p, a = best(S, v, T, h, D, k)
        rows[name] = dict(v=v, T=T, h=h, D=D, k=k, x=round(D / v, 4), C=round(C, 8),
                          ratio=round(C / rec, 4), p=p, a=a, source=src)
    out['systems'] = rows
    # 4. dense units at the Theorem B cap, k = T, 2T, 3T deleted lines (T = 8 is w.l.o.g.)
    capped = {}
    for h in range(3, 10):
        r = cap(h)
        capped[h] = {'cap_v_per_T': r, 'dense_x': round(h / r, 4)}
        for m in (1, 2, 3):
            if m >= r:
                capped[h][f'k={m}T'] = None
                continue
            C = best(S, r * 8, 8, h, 8 * h, 8 * m)[0]
            capped[h][f'k={m}T'] = round(C / rec, 4)
    out['at_theorem_B_cap'] = capped
    # 5. break-even lines per dimension for k = T
    be = {}
    for h in range(3, 22):
        lo, hi = float(h), 200.0
        if best(S, hi * 8, 8, h, 8 * h, 8)[0] < rec:
            be[h] = {'v_per_T': None, 'cap': cap(h)}
            continue
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if best(S, mid * 8, 8, h, 8 * h, 8)[0] < rec else (lo, mid)
            if hi - lo < 0.005:
                break
        be[h] = {'v_per_T': round(hi, 2), 'cap': cap(h), 'dense_x': round(h / hi, 4)}
    out['break_even_k_eq_T'] = be
    return out


def main():
    S = bind()
    got = compute(S)
    path = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(got, indent=1) + '\n', encoding='utf-8', newline='\n')
        print('wrote', path)
    want = json.loads(path.read_text(encoding='utf-8'))
    assert json.loads(json.dumps(got)) == want, 'receipt mismatch'
    print('PASS_WINDOW_BREAK_EVEN_4470_MODEL_SCREEN_NO_KAPPA')


if __name__ == '__main__':
    main()
