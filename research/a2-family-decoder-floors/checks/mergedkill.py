# CHECKED fact for Case II(b) (README 4/5.3): the joint kill system of any two merged classes M_ij (X-column zeta conditions included) has solutions only on gamma_2 = gamma_3.
# Unknowns per class: a column normal (f,1), f in K^8 (one f per class); shared: gamma_2, gamma_3 and zeta_1..zeta_3.  Equations per class O:  off X, r_s.f - gamma_k (r_1.r_s) = 0 (gamma_1 = 0, k = the
# triangle line orthogonal to s);  on X, r_i.f + zeta_i = 0 for u_i in O.  We compute the exact nullspace over Q and assert every solution has gamma_2 = gamma_3.
# Consequence (README): off the B-locus gamma_2 != gamma_3 at most one column direction kills any M_ij (a direction killing M_ij also kills T_i and T_j and the unique killer of T_i is shared, so two
# different M's would share a T-killer and be killed jointly).  The census (census_facts.py, recorded logs) gives the co-killable triples.  usage: UNIT=P112|P104|E8 [A2TRI=a,b,c] python mergedkill.py
import itertools
from a2cls import *
r1 = R[Xs[0]]
def gidx(s): return [i for i in range(3) if dot(R[Xs[i]], R[s]) == 0][0]
def eqs(co):
    E = []
    for s in bits(cls[co]):
        if s in Xs:
            i = Xs.index(s); row = list(R[s]) + [0, 0] + [0, 0, 0]; row[10 + i] = Fr(1); E.append(row)
        else:
            k = gidx(s); row = list(R[s]) + [0, 0, 0, 0, 0]; c = dot(r1, R[s])
            if k == 1: row[8] = -c
            if k == 2: row[9] = -c
            E.append(row)
    return E
def system(classes):
    n = 8 * len(classes) + 5; rows = []
    for j, co in enumerate(classes):
        for e in eqs(co):
            row = [Fr(0)] * n; row[8 * j:8 * j + 8] = e[:8]; row[8 * len(classes):] = e[8:]; rows.append(row)
    ns = nullspace(rows, n)
    return len(ns), [x[8 * len(classes):] for x in ns]
print(UNIT, 'X', Xs, 'merged classes', Mg, 'triangle classes', Tg)
for m in Mg:
    d, proj = system([m])
    ok = any(q[0] != q[1] for q in proj)
    print(' single', m, 'solution dim', d, 'a solution with gamma2 != gamma3 exists:', ok)
    assert ok                                         # one merged class alone IS killable off the B-locus (that is why one M is allowed in the relaxation)
npair = 0
for a, b in itertools.combinations(Mg, 2):
    d, proj = system([a, b]); npair += 1
    print(' pair', a, b, 'solution dim', d, '(g2,g3,z1,z2,z3):', [[str(x) for x in q] for q in proj])
    assert all(q[0] == q[1] for q in proj)
d, proj = system(Mg)
assert all(q[0] == q[1] for q in proj)
print('PASS merged-kill %s %s: the joint kill system of any two merged classes (and of all three) has solutions only on gamma2 = gamma3 (%d pairs)' % (UNIT, Xs, npair))
