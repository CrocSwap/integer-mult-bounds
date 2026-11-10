#!/usr/bin/env python3
"""RELAXED per-event verifier (one line differs from verify_strict.py): the predecessor rules (native.py:52-72 / local.py:122-160), standard library.
python3 -B verify_relaxed.py data/word.json.gz   prints every rejected event as (index, rule) and the rejection count.
Rule 'move nesting' (declared change): a public MOVE must ascend, an owned MOVE must be nested in either direction; paid |delta dim| either way."""
import gzip, json, sys
from fractions import Fraction as Q
def _sm(m):
    # odd-scalar change: 2,3,5-smooth test (alphabet A = Z[1/2,1/3,1/5]); replaces the power-of-two tests of the dyadic rule
    m=abs(m)
    for p_ in (2,3,5):
        while m%p_==0:m//=p_
    return m==1
W = json.load(gzip.open(sys.argv[1], 'rt'))
def span(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
sp = [span(b) for b in W['frames']]; n = len(W['initial']); NR = n + W['owned_fields']
cur = list(W['initial']) + [None] * W['owned_fields']; owned = set(); rej = []
for i, e in enumerate(W['program']):
    op, r = e[0], e[1]
    if op == 'MOVE':
        _, r, a, b, pv = e
        if cur[r] != a or bool(pv) != (r in owned): rej.append((i, 'move current')); 
        elif not ((sp[b] < sp[a] or sp[a] < sp[b]) if pv else sp[a] < sp[b]): rej.append((i, 'move nesting'))
        cur[r] = b
    elif op == 'INIT':
        if not (r >= n and r not in owned): rej.append((i, 'init'))
        owned.add(r); cur[r] = e[2]
    elif op == 'CLEAR':
        if not (r in owned and cur[r] == e[2]): rej.append((i, 'clear'))
        owned.discard(r); cur[r] = None
    else:
        q = Q(e[2] if op == 'SCALE' else e[3]); f = e[-1]
        if q == 0 or cur[r] != f: rej.append((i, 'scalar frame')); continue
        if not _sm(q.denominator) or not abs(q) + 1 < 2 ** 16: rej.append((i, 'scalar alphabet'))
        if op == 'SCALE' and not _sm(q.numerator): rej.append((i, 'unit'))
        if op != 'SCALE' and not (e[2] != r and 0 <= e[2] < NR and cur[e[2]] == f): rej.append((i, 'scalar source'))
print('rejected events:', len(rej), sorted({x[1] for x in rej}), 'indices', ' '.join(str(x[0]) for x in rej))
print('REJECTED_RELAXED' if rej else 'ACCEPTED_RELAXED')
