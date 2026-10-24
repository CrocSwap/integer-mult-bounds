"""Admissible puncture sets of PR555's L3 generator for a plan_thirds seed: nine eligible lines (gen_p3.eligible), one
per 4-frame, classes affinely independent in E8/2E8 (the rule of research/e8-bit-p111/discovery/choose.py)."""
import itertools, random
import h8lib as H
import e8  # imported by gen_p3 from research/e8-bit-carrier-skeleton/code/skeleton
from geom import Geom
from planio import load_plan


def rank(vecs):
    basis = []
    for v in vecs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def admissible(seed):
    V, GI = e8.V, e8.GI
    brow = [sum((int(GI[t, b]) & 1) << b for b in range(V)) for t in range(V)]
    G, sol = Geom(), load_plan(str(H.PLAN))
    freeline, assign = H.gen_p3.plan_thirds(G, sol, random.Random(seed))
    dcellof, keepline, home, qhostD6, zz = H.gen_p3.derive(G, sol, freeline)
    elig = [p for p in range(8, V) if H.gen_p3.eligible(G, sol, dcellof, keepline, qhostD6, zz, p)[0]]
    byframe = {}
    for p in elig:
        byframe.setdefault(G.phi[p], []).append(p)
    out = []
    for fs in itertools.combinations(sorted(byframe), 9):
        for P in itertools.product(*(byframe[f] for f in fs)):
            if rank([(1 << V) | brow[p] for p in P]) == 9:
                out.append(sorted(P))
    return sorted(out)
