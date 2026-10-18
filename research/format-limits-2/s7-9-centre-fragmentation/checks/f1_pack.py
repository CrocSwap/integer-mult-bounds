"""F1: format-level lower bound on target fragmentation (port of cards B85). Exact maximum 'last-reader' packing by MILP."""
import math
from collections import defaultdict, Counter
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from common import *
psi = lambda r: r * math.log(73 / r)
d = jgz('pr656-k492audit-pr622-ck-CANONICAL-WORD.json.gz'); v = d['v']
isT = lambda r: v <= r < 2 * v
reads = defaultdict(set); tre = defaultdict(set)
for p in ('A', 'B'):
    for e in d[p]:
        if e[0] != 'add': continue
        a, b = e[1], e[2]
        if isT(a) and not isT(b): reads[b].add(a); tre[a].add(b)
        elif isT(b) and not isT(a): reads[a].add(b); tre[b].add(a)
check('f1.pack.targets-operands-pairs', (len(tre), len(reads), sum(map(len, reads.values()))) == (112, 396, 796))
check('f1.pack.reader-count-hist', sorted(Counter(len(s) for s in reads.values()).items()) == [(1, 220), (2, 64), (3, 24), (4, 64), (5, 24)])
T = sorted(tre); ix = {t: i for i, t in enumerate(T)}
edges = set()
for o, st in reads.items():
    for a in st:
        for b in st:
            if a < b: edges.add((ix[a], ix[b]))
A = np.zeros((len(edges), len(T)))
for k, (a, b) in enumerate(edges): A[k, a] = A[k, b] = 1
r = milp(-np.ones(len(T)), constraints=LinearConstraint(A, -np.inf, 1), integrality=np.ones(len(T)), bounds=Bounds(0, 1), options={'time_limit': 40})
P = int(round(-r.fun))
check('f1.pack.milp-optimal', r.status == 0, f'status {r.status} ({r.message}); max independent set P={P}')
g = min(psi(a) + psi(8 - a) for a in range(1, 8)) - psi(8)
check('f1.pack.stop-cost-3.014', abs(g - 3.01416129) < 1e-6, f'{g:.6f}')
bound = g * (len(T) - P)
print(f'   bound g*(112-P) = {bound:.2f} psi/call (P={P}); published run: P>=36 by time-capped search -> 229.08')
check('f1.pack.bound-at-most-229.08', bound <= 229.08 + 1e-6 and P >= 36, f'{bound:.2f}')
done()
