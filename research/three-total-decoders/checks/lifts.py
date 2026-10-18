"""Group G2.nojoint-lifts: the explicit same-support rational lifts in data/lifts_nojoint.json (made by scripts/make_lifts.py, an exact gauge-fixed
minor search in the manner of card g1/exactlift.py).  For each stored (configuration, minimiser g, rational matrix M):
 g is a cost-minimiser (exhaustive minimum recomputed; for the gadget the recorded minimum 19 is used), supp M = supp B (ones of B, diagonal included),
 the diagonal of M is nonzero, and the exact Fraction block ranks of M are <= the F2 block ranks of B (all Lemma B needs); equality is reported."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from kit import *
L = json.load(open(os.path.join(DATA, 'lifts_nojoint.json')))
cache = {}; ok_min = ok_supp = ok_diag = ok_le = ok_eq = 0; byc = {}
for e in L:
    n = e['config']
    if n not in cache:
        P, Q = load_cfg(n); R, A, free = setup(P, Q)
        cache[n] = (P, Q, R, A, free, 19 if n == 'gad.json' else enum(P, Q)[0])
    P, Q, R, A, free, best = cache[n]; v = len(P)
    B = tomat(e['g'], free, v); M = e['lift']; fr = blockranks(B, R, A); qr = block_q(M, R, A)
    ok_min += (sum(fr) == best); ok_supp += all((M[t][s] != 0) == bool(B[t][s]) for t in range(v) for s in range(v))
    ok_diag += all(M[t][t] != 0 for t in range(v)); ok_le += all(a <= b for a, b in zip(qr, fr)); ok_eq += (qr == fr)
    byc[n] = byc.get(n, 0) + 1
n = len(L)
print("NL lifts: %d stored (%d configurations: cex_joint_v7 all 4 minimisers, nojoint_21_1..14 the first <= 12 minimisers by ones count, gad.json 8 sampled non-TS minimisers); minimiser %d, support equal %d, diagonal nonzero %d, exact Q block ranks <= F2 ranks %d (equal %d) of %d" % (
    n, len(byc), ok_min, ok_supp, ok_diag, ok_le, ok_eq, n))
print("NL cex_joint_v7 minimisers lifted: %d of 4" % byc.get('cex_joint_v7.json', 0))
