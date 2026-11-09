#!/usr/bin/env python3
"""Added proof check for the BIT saving 0.00385248 of research/bit-chain-nested-root: actual 134-axis geometry.
Python 3.12, standard library. It reads only BIT-CHAIN-ADMISSION.json of that package and changes nothing in it.
Expected marker: PASS_AMBIENT_134_FOR_BIT_CHAIN_NESTED_ROOT"""
import json
from fractions import Fraction as Q
from pathlib import Path
A = json.loads((Path(__file__).resolve().parents[2] / 'BIT-CHAIN-ADMISSION.json').read_text())
T = {int(k): v for k, v in A['targets'].items()}; P = {int(k): v for k, v in A['paid'].items()}
TESTED = Q('.0038525'); GAP = Q(1, 10**10); V = 768; n = 111; F = 18; D = A['details']; ev = D['binary_events']


def need(ok, m):
    if not ok: raise ValueError(m)


G = 10**100
def down(x): return Q((x * G).__floor__(), G)
def up(x): return Q(-((-x * G).__floor__()), G)


def atanh2(z, N=90):
    z = Q(z); s = Q(0); p = z; zz = z * z
    for k in range(N):
        s += p / (2 * k + 1); p = up(p * zz) if z > 0 else down(p * zz)
    r = 2 * abs(z)**(2 * N + 1) / (1 - zz); return down(2 * s - r), up(2 * s + r)


LN2 = atanh2(Q(1, 3))
def ln(r):
    k = r.bit_length(); x = Q(r, 2**k); a = atanh2((x - 1) / (x + 1)); return k * LN2[0] + a[0], k * LN2[1] + a[1]


def log_power(C, A0, d=43, v=V):
    """Least p with theta^p<eta=t*A0^(-v*C) and A0^(v*C)<2^p, theta=(d-1)/d, by exact logarithm enclosures."""
    t = 1 - C; la = ln(A0); b = (v * C * la[0], v * C * la[1]); c = 1 - t
    lt = (-c - c * c, -c); th = -sum(Q(1, d)**k / k for k in range(1, 200))
    p = 1
    while not (p * th < lt[0] - b[1] and b[1] < p * LN2[0]): p += 1
    return p


def grid(p):
    s = GAP.denominator; lo, hi = 1, 2
    while not (s * hi + 1)**p < 2**hi: lo, hi = hi, hi * 2
    while hi - lo > 1:
        m = (lo + hi) // 2
        if (s * m + 1)**p < 2**m: hi = m
        else: lo = m
    need(not (s * (hi - 1) + 1)**p < 2**(hi - 1), 'preceding grid fails'); return hi


# controls: the original certificate of this package and both published values of the retained audit
need(log_power(TESTED, 127) == A['finite_admission']['uniform_compiler']['logarithm_power'] == 610, 'reproduces the committed 127-axis power')
need(log_power(Q('.00376670'), 127) == 596 and log_power(Q('.00376670'), 134) == 603, 'reproduces the audit values for the other source')
need(A['finite_admission']['ambient'] == '127^768', 'the committed certificate is at 127')
need(2 * 15**(V * 43) <= 134**(V * 42) and 15**43 < 16**42, 'exit comparison at 134 axes')
p = log_power(TESTED, 134); need(p == 617 and log_power(TESTED, 134) > 610, 'repaired power'); j = grid(p); H = GAP.denominator * j
need((H + 1)**p < 2**j, 'uniform threshold')
route_count = 4 * (sum(P.values()) + sum(T.values())) + 8 * n * F + 8 * n * ev['IDLE_ONE']; routes = 8 * (10 * 134**2 + 10 * 134) * route_count
visible = D['visible_records']; need(routes + visible < 10**12, 'ordinary work funded at 134 axes'); need(routes == route_count * 1447200, 'route charge')
need(max(T) == 127 and D['owned_bank_bound'] < 10**7, 'largest target and owned bank')
# ordinary completion from the canonical admitted backend, with no step from an unreviewed intermediate
rho = Q(1, 250); cov = TESTED - 2 * GAP; b = Q('.0034'); rows = []
for adm in (Q('.00385'), Q('.00385248')):
    a = (1 - rho) * cov + rho * b; need(b < adm < a < cov < rho < 1 - a, 'wrapper gaps'); rows.append((str(float(b)), str(float(adm)), str(a - adm))); b = adm
print('PASS_AMBIENT_134_FOR_BIT_CHAIN_NESTED_ROOT')
print(json.dumps(dict(ambient=134, theta='42/43', logarithm_power=p, committed_power_at_127=610, grid_index=j, H=H, route_count=route_count, routes=routes, visible=visible, total=routes + visible, owned_bank=D['owned_bank_bound'], wrapper=rows), indent=1))
