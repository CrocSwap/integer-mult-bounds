"""Corollary J (B-independent first-order jet test, no-wild class) on: all 4095 sub-configurations of tied_min; a seeded sample of random all-harmonic configurations
(same generator as scripts/t16.py).  For each configuration: classify (no wild incidence), phi with random z_p over GF(2^16) (preserving binomial incidences), exact order-0 checks
(incidences 0, harmonic diagonals 0, other diagonals != 0), then (J1) solved as a nullspace over GF(2^16) and every (J2) functional tested for being non-zero on it
(over the algebraic closure this gives one jet satisfying all of (J2), see README).  A pass is a certificate that (A) holds for the configuration for every B."""
import itertools, random, collections, sys
from common import *
from kit import *; from phi import *; from tangent import tangent_cr2; from gen import prim
def jtest(P, Q):
    v = len(P); R, A, free = setup(P, Q)
    pi = [{j for j in range(3) if P[t][j]} for t in range(v)]; sig = [{j for j in range(3) if Q[t][j]} for t in range(v)]
    w, H = classify(P, Q)
    if w: return 'wild'
    phi = make_phi(random.Random(12345)); Pt = [[phi(x) for x in p] for p in P]; Qt = [[phi(x) for x in q] for q in Q]
    if not all(dot2(Pt[t], Qt[s]) == 0 for (t, s) in free): return 'order0-incidence'
    dz = [t for t in range(v) if dot2(Pt[t], Qt[t]) == 0]
    if dz != H: return 'order0-diagonal'
    res, dim = tangent_cr2(Pt, Qt, pi, sig, free, H)
    return 'ok' if all(res.values()) else 'fail'
P0, Q0 = load_cfg('tied_min.json'); st = collections.Counter()
for m in range(1, 13):
    for S in itertools.combinations(range(12), m):
        st[jtest([P0[i] for i in S], [Q0[i] for i in S])] += 1
report('J all 4095 sub-configurations of tied_min pass the jet test (hence cost >= |W| for every B on each)', dict(st) == {'ok': 4095}, str(dict(st)))
def harm(p, k):
    i, j = [x for x in range(3) if x != k]; q = [0, 0, 0]; q[i] = p[j]; q[j] = p[i]; return prim(q)
random.seed(11); st = collections.Counter(); N = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
for it in range(N):
    r = random.choice([2, 3, 5]); E = random.choice([1, 2, 3])
    pool = list({tuple(prim([random.choice([1, -1]) * r ** random.randint(0, E), random.choice([1, -1]) * r ** random.randint(0, E), random.choice([1, -1]) * r ** random.randint(0, E)])) for _ in range(random.randint(3, 8))})
    v = random.randint(4, 14); P = []; Q = []
    for _ in range(v):
        p = list(random.choice(pool)); k = random.randrange(3); P.append(p); Q.append(harm(p, k))
    st[jtest(P, Q)] += 1
report('J %d random all-harmonic configurations (v = 4..14, entries +-r^a) pass the jet test (the 1500 of the working notes)' % N, dict(st) == {'ok': N}, str(dict(st)))
done()
