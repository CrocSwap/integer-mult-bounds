#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Crossing caps and the Floor lemma on a real caller (CALLEROPEN, an outside-session lane of DreamingOfClouds)
[C exact mod p].  Standard library only.  On the BUILT #7113 B program (default; any caller in #7113 format via argv) compute, per call k,
the end-referred x/y spans (sl_lib = copy of CALLEROUT/sl_check.py) and check:
 (1) Lemma C: rank(Y_k, Y_k+1 restricted to S = Z_k cap Z_k+1) and rank(X_k, X_k+1 | S)  -> crossing cap |S| - rank;
 (2) Floor lemma: rank(X of left calls <= k, plus the hub coordinate vectors) = 2(k+1) + 2 <= |Z_k|  (and right arm mirrored);
 (3) the B idle crossings actually used (from the IDLE runs) vs the cap.  Random D, q0 = 1 and i."""
import gzip, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sl_lib import *  # noqa: E402,F403
def spans(C, part, q0, seed=7):
    n = C['roles']; rnd = random.Random(seed); Dv = {s: rnd.randrange(2, P) for s in range(1, 18)}
    R = ident(n); snaps = {}; order = []
    for e in C['events']:
        if e[0] == 'J':
            apply_native(R, C, e, q0, Dv, 'A'); apply_native(R, C, e, q0, Dv, 'B'); snaps[e[1]] = (e, [r[:] for r in R]); order.append(e[1])
        else: apply_op(R, e, q0, Dv)
    F = R; T = C['types'][part]; off = T['offset']; m = len(T['diagonal'])
    masks = {k: {off + i for i, dg in enumerate(T['diagonal']) if dg[1 + k]} for k in range(1, 18)}
    XS = {}; YS = {}
    for k, (e, Rk) in snaps.items():
        Jp = ident(n); apply_native(Jp, C, e, q0, Dv, part); Jm = ident(n); apply_native(Jm, C, e, (P - q0) % P, Dv, part)
        s = matmul(Jp, inv(Jm)); S = matmul(F, inv(Rk)); E = [[(s[i][j] - (i == j)) % P for j in range(n)] for i in range(n)]
        Ee = matmul(matmul(S, E), inv(S))
        XS[k] = basis([list(c) for c in zip(*Ee)]); YS[k] = basis(Ee)
    return order, masks, XS, YS, off, m
def restrict(vecs, S): return [[v[i] for i in sorted(S)] for v in vecs]
ARGS = sys.argv[1:] or [str(HERE / 'data' / 'caller-7113.json.gz'), 'B']
for fn, part in zip(ARGS[::2], ARGS[1::2]):
    with (gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)) as fh:
        C = json.load(fh)
    for q0 in (1, IM):
        order, Z, XS, YS, off, m = spans(C, part, q0)
        hubs = [r for r in range(off, off + m) if all(r in Z[k] for k in range(1, 18))]
        print('%s part %s q0=%s: call order %s; hubs %s; |Z| %s' % (fn.split('/')[-1], part, 'i' if q0 == IM else q0, order == sorted(order), [h - off for h in hubs], [len(Z[k]) for k in order]))
        line = []
        for a, b in zip(order, order[1:]):
            S = Z[a] & Z[b]
            ry = rank(restrict(YS[a] + YS[b], S)); rx = rank(restrict(XS[a] + XS[b], S))
            line.append('%d|%d:S%d ry%d rx%d cap%d' % (a, b, len(S), ry, rx, len(S) - max(rx, ry)))
        print('  boundaries:', ', '.join(line))
        # floor lemma: left arm = calls whose mask grows; use first half where |Z| increases
        sizes = [len(Z[k]) for k in order]; peak = sizes.index(max(sizes))
        fl = []
        for i in range(len(order)):
            k = order[i]; A = order[:i + 1] if i <= peak else order[i:]
            vec = sum((XS[j] for j in A), []) if i <= peak else sum((YS[j] for j in A), [])
            hv = [[int(c == h) for c in range(len(vec[0]))] for h in hubs]
            fl.append('%d:%d/%d/%d' % (k, rank(vec), rank(vec + hv), len(Z[k])))
        print('  floor (rank X_arm<=k / +hubs / |Z_k|):', ' '.join(fl), flush=True)
