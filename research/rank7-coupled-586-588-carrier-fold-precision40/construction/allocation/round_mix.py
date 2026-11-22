#!/usr/bin/env python3
"""round_mix.py USAGE.json T OUT.json [--lam 1000] -- integer pattern mix closest to a fractional chronological LP usage (diag_lp free mode):
minimize sum_p H_idle(p)(b) n_p + lam * sum_p |n_p - u_p| subject to exact bin counts per capacity (112*T*{6,4,4,4}) and exact width totals
(inventory * 9T); patterns = LP support plus single residues and empties. Output = PATTERNS.json-style {widths, target} for fill17 --mix-file."""
import json, sys, argparse, itertools
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import relax as X
ap = argparse.ArgumentParser(); ap.add_argument('usage'); ap.add_argument('T', type=int); ap.add_argument('out'); ap.add_argument('--lam', type=float, default=1000.0)
ap.add_argument('--inventory', required=True, help='JSON per-call inventory'); ap.add_argument('--scale', type=float, default=1.0, help='usage multiplier (e.g. 2 to map a T37 usage to T74)')
a = ap.parse_args()
u = json.load(open(a.usage)); W = [int(w) for w in u['widths']]; b = u['b']
inv = {int(k): v for k, v in json.loads(a.inventory).items()}
use = {}
for name, x in u['usage'].items():
    cap, spec = name.split(':'); ws = [] if spec == 'empty' else [int(z) for z in spec.split('+')]
    use[(int(cap), tuple(ws.count(w) for w in W))] = x * a.scale
pats = set(use)
for cap in X.BINS:
    for i, w in enumerate(W):
        if w <= cap:
            pats.add((cap, tuple(int(j == i) for j in range(len(W)))))
    pats.add((cap, tuple(0 for _ in W)))
pats = sorted(pats)
n = len(pats)
idle = [cap - sum(w * k for w, k in zip(W, q)) for cap, q in pats]
c = [X.Hfloat(r, b) for r in idle] + [a.lam] * (2 * n)
caps = sorted(X.BINS)
A = np.zeros((len(caps) + len(W) + n, 3 * n)); lo = []; hi = []
for j, (cap, q) in enumerate(pats):
    A[caps.index(cap), j] = 1
    for i, k in enumerate(q):
        A[len(caps) + i, j] = k
rhs = [X.BINS[cap] * a.T for cap in caps] + [inv[w] * 9 * a.T for w in W]
lo += rhs; hi += rhs
for j in range(n):   # n_j - u_j = p_j - m_j
    r = len(caps) + len(W) + j
    A[r, j] = 1; A[r, n + j] = -1; A[r, 2 * n + j] = 1
    lo.append(use.get(pats[j], 0.0)); hi.append(use.get(pats[j], 0.0))
res = milp(np.array(c), integrality=np.array([1] * n + [0] * (2 * n)), bounds=Bounds(0, np.inf), constraints=LinearConstraint(A, lo, hi), options={'time_limit': 120, 'mip_rel_gap': 0})
assert res.x is not None, res.message
xi = np.rint(res.x[:n]).astype(int)
target = [[cap, list(q), int(x)] for (cap, q), x in zip(pats, xi) if x]
json.dump(dict(widths=W, target=target, source=a.usage, lam=a.lam, T=a.T), open(a.out, 'w'))
print({('%d:%s' % (cap, '+'.join(str(w) for w, k in zip(W, q) for _ in range(k)) or 'empty')): x for cap, q, x in target})
print('deviation from LP usage', round(float(sum(abs(xi[j] - use.get(pats[j], 0.0)) for j in range(n))), 3))
