#!/usr/bin/env python3
"""[C] exact + [P] arithmetic: tightness cannot be dropped from the Q = 0 caller bound (notes/tightpad.md).
(1) The direct sum of m copies of the legal Q = 0 word C1 (k = 3, n = 4) is built explicitly (registers 4c+r, stages 3c+s,
    masks shifted) and replayed by q0_callers/check.py (legality at 4 q, symbolic D): m = 2, 3 are LEGAL, n + 2 < 2k,
    and chat = the k-weighted mean of the copies' chat = chat(C1).
(2) HP(3m) < chat(C1) first at m = 109 (HP(327) = 107.902838, HP(324) is not below it), 50-digit decimal.
Standard library only."""
import copy, json, os, sys
from decimal import Decimal, getcontext
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..', 'q0_callers'))
import check as qc
getcontext().prec = 50


def direct_sum(C, m):
    n, k = C['roles'], C['stages']
    ev, dg = [], []
    for c in range(m):
        for e in C['events']:
            e = copy.deepcopy(e)
            op = e[0]
            if op == 'ADD': e[1] += n * c; e[2] += n * c
            elif op == 'SCALE': e[1] += n * c
            elif op == 'LAMBDA': e[1] += n * c
            elif op == 'HOST': e[1] += k * c; e[2] += n * c; e[3] += n * c
            elif op == 'IDLE_ONE': e[1] += n * c; e[2] = [x + k * c for x in e[2]]
            ev.append(e)
        for r in C['diagonal']:
            dg.append(r[:2] + [0] * (k * c) + r[2:2 + k] + [0] * (k * (m - 1 - c)) + r[2 + k:])
    return {'schema': C['schema'], 'roles': n * m, 'stages': k * m, 'events': ev, 'diagonal': dg}


def HPd(k):
    s = Decimal('0.99')
    p = lambda x: (s * Decimal(x).ln()).exp()
    return Decimal(208) / k * ((k - 2) * (p(17) - p(16)) + p(8 * k + 1) - p(8) * k)


C1 = json.load(open(os.path.join(H, '..', 'q0_callers', 'caller_C1.json')))
c1 = qc.chat(C1)
for m in (2, 3):
    W = direct_sum(C1, m)
    ok, wf = qc.legal(W)
    assert ok and wf, m
    assert W['roles'] + 2 < 2 * W['stages']          # not tight: n + 2 < 2k
    assert abs(qc.chat(W) - c1) < 1e-9, (qc.chat(W), c1)
    print('direct sum m=%d: n=%d k=%d LEGAL, chat=%.6f = chat(C1)' % (m, W['roles'], W['stages'], qc.chat(W)))
cd = Decimal(repr(c1))
assert HPd(327) < Decimal('107.910089') < HPd(324) and abs(float(HPd(327)) - 107.902838) < 1e-6
assert all(HPd(3 * m) > Decimal('107.9100890') for m in range(2, 109))
assert abs(c1 - 107.910089) < 1e-6
print('HP(324) = %.6f, HP(327) = %.6f < chat(C1) = %.6f' % (HPd(324), HPd(327), c1))
print('PASS direct-sum tightness witnesses')
