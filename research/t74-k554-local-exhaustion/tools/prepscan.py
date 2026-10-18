"""For every B read with a negative deletion relaxation, test whether its exact effect avoids target rows (a precondition for
compensating it in the frame-free cleanup prepends). usage: prepscan.py RELAX-B.json"""
import json, gzip, sys
from fractions import Fraction as Q
import _paths
w = json.load(gzip.open(_paths.BASE))
B = w['B']; tails = [w['cleanup'][i] for i, U in w['early_cleanup']]; seq = B + tails; NB = len(B); L = len(seq)
V = 112; low = set(map(int, w['helper_final']))
res = {int(k): v for k, v in json.load(open(sys.argv[1])).items()}
coef = lambda g: Q(g[3], g[4]) if g[0] == 'add' else Q(g[2], g[3])
cols = {}; colsB = {}
S = lambda x: cols.get(x, {x: Q(1)}); SB = lambda x: colsB.get(x, {x: Q(1)})
info = {}
def step(c, Sf, g):
    if g[0] == 'add':
        t, s = g[1], g[2]; k = coef(g); a = dict(Sf(s))
        for r, v in Sf(t).items():
            a[r] = a.get(r, 0) + k * v
            if not a[r]: del a[r]
        c[s] = a
    else:
        x = g[1]; c[x] = {r: v * coef(g) for r, v in Sf(x).items()}
for i in range(L - 1, -1, -1):
    g = seq[i]
    if i < NB and g[0] == 'add' and res.get(i, {}).get('delta', 0) < 0:
        t = g[1]
        info[i] = (dict(S(t)), {r: v for r, v in SB(t).items() if V <= r < 2 * V})
    step(cols, S, g)
    if i < NB: step(colsB, SB, g)
fe = lambda r: r < V or (r >= 2 * V and r not in low)
ok = []
for i, (d, dB) in info.items():
    tgt = [r for r in d if V <= r < 2 * V]
    nonfull = [r for r in d if not fe(r) and not (V <= r < 2 * V)]
    if not dB and not tgt:
        ok.append((i, B[i][:5], res[i]['delta'], len(d), nonfull))
print('gates with gain', len(info), 'with no target rows', len(ok))
for o in sorted(ok, key=lambda x: x[2])[:40]: print(o)
