#!/usr/bin/env python3
"""[C] exact: the TIGHT55 cube partition (global d-lex-leader + one cube per orbit-lexmax inactive set I) has a gap.
A vector d in {0..9}^16 (d_j = dim U_j^perp, 9 = inactive) satisfying all 384 lex-leader constraints d >= d o p can have an
inactive set I = {j : d_j = 9} that is NOT lexmax in its own orbit, so it is not among the 401 stored representatives
(the scheme covered 402 cubes = 401 + empty).  Witnesses: the two vectors below.  Standard library only.
This is a SAT-methodology note: it shows why symmetry breaking must be done per cube with the stabiliser of I."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(H, 'perms.json')))['perms']
R = set(json.load(open(os.path.join(H, 'reps.json')))['reps'])
act = lambda d, p: tuple(d[p[j]] for j in range(16))
WIT = {1091: (9, 9, 8, 6, 6, 8, 9, 4, 4, 2, 9, 0, 5, 6, 8, 8), 33: (9, 8, 8, 8, 7, 9, 8, 8, 7, 7, 8, 7, 8, 7, 7, 8)}
assert len(P) == 384 and all(sorted(p) == list(range(16)) for p in P)
for I, d in WIT.items():
    assert all(d >= act(d, p) for p in P), 'witness violates a lex-leader constraint'
    assert sum(1 << j for j in range(16) if d[j] == 9) == I
    ind = tuple(1 if I >> j & 1 else 0 for j in range(16))
    assert any(act(ind, p) > ind for p in P), 'I is lexmax in its orbit'   # so I is not an orbit-lexmax representative
    assert I not in R
print('PASS tight55 symmetry-gap witnesses: masks', sorted(WIT), 'satisfy all 384 lex-leader constraints but are not orbit-lexmax')
