# The A2 realisations are NOT of B-form (CONJB section 1.3), exact certificate on A2 members of UNIT.  B-form: M = D1 G D2 + c beta^T with c_u beta_s = 0 on orthogonal pairs.
# Steps (see README): (1) the common non-orthogonal neighbourhood of Nbar[u] is {u} for every line u (exact);
# (2) Sigma = {u : dim N_u >= 2}, N_u = b(O_u)^perp, equals X; the rows off Sigma span 8 dimensions, so pi is unique and supp(A pi) = X;
# (3) rank b(union of O_u over u in X) = 9, so no nu exists.  Also: deleting any single row leaves rank 9 (case "dim N_u = 1" of the proof).
# Ranks are computed mod p = 2^61-1 (a lower bound for the rank over Q; every inference uses only lower bounds, or upper bounds that hold by construction).
# Arguments: none = 3 random members (seeds as in a2fam.py logic); 'tie' = the special member of the tie decoder of the given unit (data/tie_<UNIT>.json).
import sys, json, os, random
from a2lib import *
from modrank import rkp
rk=lambda rows: rkp(rows) if rows else 0
Nb=[[s for s in range(v) if Gm[u][s]!=0] for u in range(v)]
CN1=[[w for w in range(v) if all(Gm[w][s]!=0 for s in Nb[u])] for u in range(v)]
assert all(CN1[u]==[u] for u in range(v)), 'CN(Nbar[u]) != {u}'
print('PASS common non-orthogonal neighbourhood of Nbar[u] is {u} for all',v,'lines, unit',UNIT)
Ou=[[s for s in range(v) if Gm[u][s]==0] for u in range(v)]
def certify(M,label):
    Mt=[list(c) for c in zip(*M)]
    assert pattern_ok(M)==0
    r=rk(M); assert r==9, r
    dimN=[9-rk([Mt[s] for s in Ou[u]]) for u in range(v)]
    Sa=[u for u in range(v) if dimN[u]>=2]
    off=[u for u in range(v) if u not in Sa]
    r_off=rk([M[u] for u in off])
    r_minus1=min(rk([M[w] for w in range(v) if w!=u]) for u in range(v))
    assert r_minus1==9
    base=r_off
    supp=[u for u in range(v) if rk([M[w] for w in off]+[M[u]])>base]
    U=sorted(set(s for u in supp for s in Ou[u])); rU=rk([Mt[s] for s in U])
    print('  %s: rank %d, Sigma_a=%s, rank rows off Sigma_a=%d, min rank deleting one row=%d, supp(A pi)=%s, rank b(union O_u)=%d'%(label,r,Sa,r_off,r_minus1,supp,rU))
    assert sorted(Sa)==sorted(X) and r_off==8 and sorted(supp)==sorted(X) and rU==9
    print('PASS %s: not of B-form (rank b(union_{u in X} O_u) = 9, so no nu)'%label)
if len(sys.argv)>1 and sys.argv[1]=='tie':
    D=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data','tie_%s.json'%UNIT)))
    th=tuple(Fr(x) for x in D['theta']); zX=tuple(Fr(x) for x in D['zX'])
    A,B=build(th,zX); certify(Mof(A,B),'tie-decoder member %s'%UNIT)
else:
    rnd=random.Random(1); good=0
    while good<3:
        th=tuple(Fr(rnd.randint(-9,9)) for _ in range(4)); zX=tuple(Fr(rnd.randint(-50,50),rnd.randint(1,7)) for _ in range(3))
        A,B=build(th,zX); M=Mof(A,B)
        if pattern_ok(M)!=0: continue
        good+=1; certify(M,'member %d'%good)
