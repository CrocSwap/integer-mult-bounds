"""Owner-fill pattern relaxation (r8 B/G model, r9 relax_r9.py) on the r10 candidate (#2751 + #2766 refit + five
retired-lender aliases).  Value map: marginal relaxed endpoint gain of removing ONE helper of width w, with the local
profile losing that helper's mass either as one rank-w entry ('entry', r8 convention, only if local has rank w) or as
w rank-1 entries ('unit', optimistic), and the realized-equals-relaxed check of the current state.
usage: venv-python -I relax_r10.py OUT.json"""
import json, sys, itertools
from collections import Counter
import numpy as np, mpmath as mp
from scipy.optimize import milp, LinearConstraint, Bounds
mp.mp.dps = 60
M, W, CALLS = 73, 66304, 666
NB = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
WID = (4, 5, 7, 8, 9)
C_REF = mp.mpf('0.001717409316335491643448458477541172229282')
LOC = {1: 2382, 2: 648, 3: 268, 4: 128, 5: 26, 8: 8}
INV = {4: 26, 5: 2, 7: 62, 8: 78, 9: 240}
IDLE_PUB = {1: 17316, 3: 6594, 5: 9878, 32: 1, 48: 26558}
def root(counts):
    f = lambda a: mp.fsum(n * mp.power(mp.mpf(r) / M, 1 - a) for r, n in counts.items() if r) - W
    return mp.findroot(f, (mp.mpf('0.0016'), mp.mpf('0.0018')), solver='anderson')
def glob(loc, idle):
    c = Counter({r: CALLS * n for r, n in loc.items()}); c.update(idle); return dict(sorted(c.items()))
pats = [(R, p) for R in NB for k in range(0, R // 4 + 1) for p in itertools.combinations_with_replacement(WID, k) if sum(p) <= R]
def solve(inv, a):
    h = lambda r: float(mp.power(mp.mpf(r) / M, 1 - a)) if r else 0.0
    c = np.array([h(R - sum(p)) for R, p in pats]); A = []; lo = []
    for R in NB: A.append([1.0 if q == R else 0.0 for q, p in pats]); lo.append(NB[R])
    for w in WID: A.append([float(p.count(w)) for q, p in pats]); lo.append(CALLS * inv.get(w, 0))
    A = np.array(A); lo = np.array(lo, dtype=float)
    r = milp(c, constraints=LinearConstraint(A, lo, lo), integrality=np.ones(len(pats)), bounds=Bounds(0, np.inf),
             options=dict(mip_rel_gap=0.0, time_limit=300, disp=False))
    assert r.status == 0, r.message
    x = np.rint(r.x).astype(int); assert np.array_equal(A @ x, lo)
    idle = Counter()
    for (R, p), n in zip(pats, x):
        if n and R - sum(p): idle[R - sum(p)] += int(n)
    return dict(sorted(idle.items()))
def best(loc, inv, a0):
    a = a0
    for it in range(6):
        idle = solve(inv, a); b = root(glob(loc, idle))
        if abs(b - a) < mp.mpf('1e-16'): break
        a = b
    return idle, b
# J-dim1: value of hosting k entering width-8 followers in width-4 cold hosts (host -> width 9), with local variants
b_pub = root(glob(LOC, IDLE_PUB)); idle0, b0 = best(LOC, INV, b_pub)
print('base realized', mp.nstr(b_pub, 22), 'relaxed', mp.nstr(b0, 22), flush=True)
out = {}
for k in (1, 2, 4):
    for name, dl in (('-H3', {3: -1}), ('-H2-H1', {2: -1, 1: -1}), ('-3H1', {1: -3}), ('-H4+H1', {4: -1, 1: 1})):
        inv = dict(INV); inv[4] -= k; inv[8] -= k; inv[9] += k
        loc = dict(LOC)
        for r, d in dl.items(): loc[r] = loc.get(r, 0) + k * d
        idle, b = best(loc, inv, b0)
        out[f'{k}:{name}'] = dict(value=mp.nstr(b - b_pub, 8), idle=idle)
        print('hostings', k, 'local', name, 'value vs realized', mp.nstr(b - b_pub, 6), 'idle', idle, flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
