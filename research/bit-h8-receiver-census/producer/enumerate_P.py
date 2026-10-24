"""All admissible puncture sets P for the shipped L3 plan with plan_thirds seed SEED (PR555 discovery/choose.py logic:
nine eligible lines outside 0..7, one per 4-frame, classes affinely independent in E8/2E8).  Writes JSON with P and
choose.py's cost model."""
import itertools, json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "repo", "research", "e8-bit-p111")
sys.path.insert(0, os.path.join(PKG, "code"))
sys.path.insert(0, os.path.join(PKG, "..", "e8-bit-carrier-skeleton", "code", "skeleton"))
import e8, gen_p3
from geom import Geom
from planio import load_plan

seed = int(sys.argv[1]); out = sys.argv[2]
V = e8.V
GI = e8.GI
BROW = [sum((int(GI[t, b]) & 1) << b for b in range(V)) for t in range(V)]


def rank(vecs):
    basis = []
    for v in vecs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


G = Geom()
sol = load_plan(os.path.join(PKG, "data", "plan-l3.json"))
freeline, assign = gen_p3.plan_thirds(G, sol, random.Random(seed))
dcellof, keepline, home, qhostD6, zz = gen_p3.derive(G, sol, freeline)
elig = [p for p in range(8, V) if gen_p3.eligible(G, sol, dcellof, keepline, qhostD6, zz, p)[0]]
byframe = {}
for p in elig:
    byframe.setdefault(G.phi[p], []).append(p)
sets = []
for fs in itertools.combinations(sorted(byframe), 9):
    for P in itertools.product(*(byframe[f] for f in fs)):
        if rank([(1 << V) | BROW[p] for p in P]) == 9:
            sets.append(sorted(P))
sets.sort()
json.dump({"seed": seed, "eligible": elig, "frames": len(byframe), "sets": sets}, open(out, "w"))
print("seed", seed, "eligible", elig, "4-frames", len(byframe), "admissible P", len(sets))
