"""Group G6: S1's non-degenerate counterexample aff14 (fleet/S1.md addendum B): a K22-free admissible B on 14 distinct points and 14 distinct lines
that is NOT TU-signable, so 'non-degenerate admissible B is regular' (and hence 'L6 forces a Lemma W' signing') is false."""
import sys, os, json, itertools
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from kit import *
P, Q, B = json.load(open(os.path.join(DATA, 'aff14.json'))); n = len(P)
adm = all(B[t][t] == 1 and dot(P[t], Q[t]) != 0 for t in range(n)) and all(dot(P[t], Q[s]) == 0 for t in range(n) for s in range(n) if t != s and B[t][s])
def prop(a, b): return all(x == 0 for x in (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]))
dp = not any(prop(P[i], P[j]) for i in range(n) for j in range(i)); dl = not any(prop(Q[i], Q[j]) for i in range(n) for j in range(i))
k22 = any(B[t][s] and B[t][s2] and B[t2][s] and B[t2][s2] for t, t2 in itertools.combinations(range(n), 2) for s, s2 in itertools.combinations(range(n), 2) if len({t, t2, s, s2}) == 4)
R, A, free = setup(P, Q)
full = [j for j in range(3) if len(R[j]) == n and len(A[j]) == n]
print("NG aff14: n=%d admissible %s; points pairwise distinct %s; lines pairwise distinct %s; off-diagonal ones %d; K22 (L6 pattern, 4 distinct indices) present: %s" % (
    n, adm, dp, dl, sum(B[t][s] for t in range(n) for s in range(n) if t != s), k22))
print("NG aff14: blocks R_j x A_j equal to the whole matrix for j in %s; block ranks %s; whole B TU-signable (Camion): %s" % (full, blockranks(B, R, A), tus(B, range(n), range(n))))
