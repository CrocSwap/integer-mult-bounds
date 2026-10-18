"""F1: carrier ladders from subspace coverings (port of cards B81 gate 1).  Ports: ck word; readers: R R^T/2 on the #656 root lines."""
import itertools, random
from collections import Counter
import numpy as np
from common import *
P = jgz('pr656-k492audit-pr622-ck-CANONICAL-WORD.json.gz')['ports']
R = np.array(jgz('pr656-FULL-WORD.json.gz')['root_lines'], float)
Gm = R @ R.T / 2; nz = (Gm != 0) & ~np.eye(112, dtype=bool)
Rd = [[t for t in range(112) if nz[t, s]] for s in range(112)]
check('f1.carriers.52-readers-per-source', all(len(x) == 52 for x in Rd))
S = set(P)
check('f1.carriers.ports-are-a-cap-in-F2^9 (no three XOR to 0)', len(S) == 112 and all((a ^ b) not in S for a, b in itertools.combinations(P, 2)))
car = []
for s in range(112):
    ports = [P[t] for t in Rd[s]]; ps = set(ports); quads = set()
    for a, b, c in itertools.combinations(ports, 3):
        e = a ^ b ^ c
        if e in ps and e > max(a, b, c): quads.add(frozenset((a, b, c, e)))
    left = set(ports); n = 0; q = list(quads)
    while left:
        best = max(q, key=lambda Q: len(Q & left), default=None)
        if best and len(best & left) >= 3: left -= best
        elif len(left) >= 2: left -= set(sorted(left)[:2])
        else: left.clear()
        n += 1
    car.append(n)
m = float(np.mean(car))
check('f1.carriers.greedy-cover-14.29-carriers-per-source', abs(m - 14.2946) < 1e-3 and min(car) == 14 and max(car) == 15, f'mean {m:.4f}, min {min(car)}, max {max(car)}; lower bound 52/4 = 13 (quads are the only 4-reader flats)')
check('f1.carriers.total-1601', round(112 * m) == 1601)
done()
