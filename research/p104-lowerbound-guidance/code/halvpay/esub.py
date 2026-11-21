"""HALVPAY esub.py: potential bounds for asc56's phases on the real 104-port instance (FANOUT56 init/targets as data).
 FULL : X <q_p>,x_p -> V, x_p - y_p ; Y {0},y -> q^perp,y   (integral; REVERSE gives 104)
 USUB : X <q_p>, post-relay half state -> V, x_p - y_p ; Y as above  (the FANOUT56 U phase; R=56 there)
 RSUB : X <q_p>, x_p -> <q_p>, post-relay half state ; Y {0},y -> {0},y (relay phase, X/Y only)
 helpers dropped: unique-token start {0}/final V terms cancel their 9 public climbs exactly [P]."""
import pickle, sys, time
from fractions import Fraction as Fr
from ebound import ebound
d=pickle.load(open('f56run_nomix.pkl','rb')); I=d['init']; T=d['targets']; P=d['P']; n=9
ports=range(len(P)) if 'q96' not in sys.argv else range(96)
syms=[('x',p) for p in ports]+[('y',p) for p in ports]; cols={s:i for i,s in enumerate(syms)}
def proj(w): return {k:v for k,v in w.items() if k in cols}
def sp(vs):
    S={0}
    for v in vs:
        if v not in S: S|={x^v for x in S}
    return frozenset(S)
V=frozenset(range(512)); Z=frozenset([0])
perp=lambda q: frozenset(x for x in range(512) if bin(x&q).count('1')%2==0)
for name in ['FULL','USUB','RSUB']:
    pubs=[]
    for p in ports:
        x0={('x',p):Fr(1)}; half=proj(I[('X',p)][1]); fin={('x',p):Fr(1),('y',p):Fr(-1)}
        if name=='FULL': pubs.append((sp([P[p]]),x0,V,fin))
        if name=='USUB': pubs.append((sp([P[p]]),half,V,fin))
        if name=='RSUB': pubs.append((sp([P[p]]),x0,sp([P[p]]),half))
        y={('y',p):Fr(1)}
        pubs.append((Z,y,(perp(P[p]) if name!='RSUB' else Z),y))
    t=time.time(); print(name,'ports',len(list(ports)),ebound(pubs,n,cols),'%.1fs'%(time.time()-t),flush=True)
