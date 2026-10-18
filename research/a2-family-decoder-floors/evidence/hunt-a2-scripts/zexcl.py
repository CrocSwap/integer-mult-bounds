# pairwise compatibility of single-class z-specials (as affine functions of theta) vs the B-locus
import pickle, sympy as sp, itertools
from a2lib import *
rowspec,colspec,zspec=pickle.load(open('specall.pkl','rb'))
Oset=[set(o) for o in O]
al2,be2,al3,be3=sp.symbols('al2 be2 al3 be3')
def zreq(Kl,th):
    g=gvecs(th); S=[i for i in range(3) if X[i] in Kl]
    rows=[R[s]+[-dot(R[s],g[i])] for i in range(3) for s in Kl if s in Oset[i]]
    ns=nullspace(rows,9); part=[x for x in ns if x[8]!=0]
    p0=part[0]; p=[a/p0[8] for a in p0][:8]
    return {k:-dot(R[X[k]],p) for k in S}
ths=[(Fr(0),)*4]+[tuple(Fr(int(i==e)) for i in range(4)) for e in range(4)]
aff={}
for key,sz,S in zspec:
    if len(key)!=1: continue
    r=[zreq(bits(cls[key[0]]),th) for th in ths]
    aff[key[0]]={k_:sp.Rational(str(r[0][k_]))+sum(sp.Rational(str(r[e+1][k_]-r[0][k_]))*s_ for e,s_ in enumerate((al2,be2,al3,be3))) for k_ in r[0]}
    print(key[0],aff[key[0]])
pickle.dump({f"s{k}":v_ for k,v_ in aff.items()},open("zaff.pkl","wb"))
r3v=R[X[2]]
co3=nullspace([[r1[k],r2[k],-r3v[k]] for k in range(8)],3)[0]; co3=[x/co3[2] for x in co3]
bn=nullspace([[Fr(1),Fr(0),Fr(1),Fr(0)],[Fr(0),Fr(1),Fr(0),Fr(0)],[Fr(0),Fr(0),co3[0],co3[1]]],4)[0]
Bf=sum(sp.Rational(str(c))*s_ for c,s_ in zip(bn,(al2,be2,al3,be3)))
for a,b in itertools.combinations(aff,2):
    common=set(aff[a])&set(aff[b]); eqs=[aff[a][k]-aff[b][k] for k in common]
    sol=sp.solve(eqs,[al2,be2,al3,be3],dict=True)
    ok=[s_ for s_ in sol if sp.simplify(Bf.subs(s_))!=0]
    print('pair',a,b,'common',common,'eqs',eqs,'compatible off B-locus:',bool(ok), ok[:1])
