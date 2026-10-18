# Aut generators for P104 = E8 lines minus F0 ∪ F1. G0 = <products of two E8 reflections fixing F0 setwise> (STRAYS-MASK2 orbits.py);
# Schreier generators of the stabiliser of the frame F1 (setwise) in G0. Every generator is checked to fix F0 and F1 setwise and to preserve
# orthogonality (it is a product of reflections, so it is an isometry). Orbits under this subgroup are sound (a subgroup only adds reps).
import sys, pickle
from setup9 import *
from lib2 import E8, dot
from fractions import Fraction as Fr
F0, F1 = load_frames()
def canon(x):
    for c in x:
        if c != 0: return tuple(x) if c > 0 else tuple(-y for y in x)
idx = {canon(r): i for i, r in enumerate(E8)}
refl = []
for a in E8:
    aa = dot(a, a)
    refl.append([idx[canon([ri - Fr(2 * dot(r, a), aa) * ai for ri, ai in zip(r, a)])] for r in E8])
S0 = set(F0); gens = []
for a in range(120):
    for b in range(120):
        g = tuple(refl[a][refl[b][i]] for i in range(120))
        if set(g[i] for i in S0) == S0: gens.append(g)
gens = sorted(set(gens)); print('G0 generators', len(gens), flush=True)
comp = lambda a, b: tuple(b[a[i]] for i in range(120))      # a then b
def inv(a):
    r = [0] * 120
    for i, x in enumerate(a): r[x] = i
    return tuple(r)
ident = tuple(range(120)); x0 = frozenset(F1)
u = {x0: ident}; st = [x0]
while st:
    x = st.pop()
    for g in gens:
        y = frozenset(g[i] for i in x)
        if y not in u: u[y] = comp(u[x], g); st.append(y)
print('orbit of F1 under G0', len(u), flush=True)
sch = set()
for x, ux in u.items():
    for g in gens:
        y = frozenset(g[i] for i in x)
        s = comp(comp(ux, g), inv(u[y]))
        sch.add(s)
sch.discard(ident)
sch = sorted(sch)
for s in sch: assert set(s[i] for i in F0) == set(F0) and set(s[i] for i in F1) == set(F1)
Lr = [E8[i] for i in range(120)]
rem = set(F0) | set(F1); liv = [i for i in range(120) if i not in rem]; pos = {x: k for k, x in enumerate(liv)}
perms = sorted({tuple(pos[s[i]] for i in liv) for s in sch})
L, v, G, frames, nbar, h, basis, cls = load('P104')
for p in perms: assert all((G[p[a]][p[b]] == 0) == (G[a][b] == 0) for a in range(v) for b in range(v))
print('stabiliser generators on P104 lines', len(perms), flush=True)
inv_ = {cls[c]: c for c in cls}
def img(O, p):
    r = 0
    for t in range(v):
        if O >> t & 1: r |= 1 << p[t]
    return r
seen = {}; orbs = []
for c in sorted(cls):
    if c in seen: continue
    orb = [c]; seen[c] = 1; st = [c]
    while st:
        x = st.pop()
        for p in perms:
            y = inv_[img(cls[x], p)]
            if y not in seen: seen[y] = 1; orb.append(y); st.append(y)
    orbs.append(orb)
print('class orbits', len(orbs), [len(o) for o in orbs], flush=True)
pickle.dump({'perms': [list(p) for p in perms], 'orbs': orbs}, open('orbits_P104.pkl', 'wb'))
