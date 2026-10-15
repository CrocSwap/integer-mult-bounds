import sys;sys.path.insert(0,__import__("os").path.dirname(__import__("os").path.abspath(__file__)))
"""Rigorous class-level ceiling for the T74 alias inventory (bins 8:49728,16:33152,32:33152,48:33152; per call widths
{4:32,5:5,7:62,8:86,9:240} x 666 calls; paid profile per call fixed).  Any fill induces integer pattern counts x_{c,p};
the idle moment sum_bins phi_a(idle) is >= the LP dual value  sum_c B_c y_c + sum_w N_w pi_w  for ANY (y,pi) with
y_c + pi.p <= phi_a(idle(c,p)) for all patterns (weak duality).  We take pi from a float LP, set y_c = min_p(...) in
interval arithmetic (so feasibility is exact) and certify M(a_ub) >= 1  =>  C <= a_ub for every fill.
argv: a_ub (decimal string) [a_lo for bisection report]"""
import sys,json
from mpmath import iv,mpf,mp
import numpy as np
from scipy.optimize import linprog
iv.dps=60;mp.dps=60
W=[4,5,7,8,9];B={8:49728,16:33152,32:33152,48:33152};NC=666
from inv import PER as per;N={w:per[w]*NC for w in W}
from inv import PAID as paid
m,WW=73,66304
assert sum(B[c]*c for c in B)-sum(N[w]*w for w in W)>0
def pats(c,i=0):
    if i==len(W):yield ();return
    for k in range(c//W[i]+1):
        for r in pats(c-k*W[i],i+1):yield (k,)+r
PL=[(c,p) for c in B for p in pats(c)]
idle=lambda c,p:c-sum(a*w for a,w in zip(p,W))
def phi_f(a,f):return 0.0 if f==0 else (f/m)*(m/f)**a/WW
def phi_iv(a,f):
    if f==0:return iv.mpf(0)
    return iv.mpf(f)/m*iv.exp(a*iv.log(iv.mpf(m)/f))/WW
def certify(astr):
    af=float(astr);ai=iv.mpf(astr)
    # float LP (dual of the class LP) : max sum B y + N pi  s.t. y_c + pi.p <= phi
    caps=list(B);nv=len(caps)+len(W)
    A=[];b=[]
    for c,p in PL:
        row=[0.0]*nv;row[caps.index(c)]=1.0
        for j,k in enumerate(p):row[len(caps)+j]=k
        A.append(row);b.append(phi_f(af,idle(c,p)))
    cobj=[-B[c] for c in caps]+[-N[w] for w in W]
    S=1e6
    r=linprog(cobj,A_ub=np.array(A),b_ub=np.array(b)*S,bounds=[(None,None)]*nv,method='highs')
    assert r.status==0
    pi=[mpf(float(v))/S for v in r.x[len(caps):]]
    piv=[iv.mpf(x) for x in pi]
    y={c:None for c in caps}
    for c,p in PL:
        v=phi_iv(ai,idle(c,p))-sum(k*piv[j] for j,k in enumerate(p))
        y[c]=v if y[c] is None else iv.mpf([min(y[c].a,v.a),min(y[c].b,v.b)])
    # integrality: L = lattice spanned by the 11 zero-reduced-cost patterns Z (index 20 in Z^9).  Every fill's pattern
    # multiset sums to the target (B,N); patterns of Z are 0 in G=Z^9/L, so the remaining patterns must sum to the
    # target's class in G.  Their reduced costs are >=0, so sum_b rc_b >= shortest path 0 -> target in the Cayley graph.
    from lattice import vec,hnf,reducer
    Z=[(8,(0,0,0,1,0)),(16,(0,0,0,2,0)),(16,(0,0,1,0,1)),(32,(0,0,0,0,3)),(32,(0,0,0,4,0)),(32,(0,0,1,2,1)),(32,(0,0,2,0,2)),(32,(0,1,0,0,3)),(32,(1,0,0,0,3)),(48,(0,0,0,0,0)),(48,(0,0,0,0,5))]
    red=reducer(hnf([vec(c,p) for c,p in Z]));tgt=red([B[c] for c in caps]+[N[w] for w in W]);zero=red([0]*9)
    best={}
    for c,p in PL:
        g=red(vec(c,p))
        if g==zero:continue
        rc=mpf((phi_iv(ai,idle(c,p))-sum(k*piv[j] for j,k in enumerate(p))-iv.mpf(y[c].a)).a)
        assert rc>=0
        if g not in best or rc<best[g][0]:best[g]=(rc,(c,p,idle(c,p)))
    D={zero:(mpf(0),[])};changed=True
    while changed:
        changed=False
        for q,(dq,path) in list(D.items()):
            for g,(rc,arg) in best.items():
                z=red([u+v for u,v in zip(q,g)])
                if z not in D or dq+rc<D[z][0]:D[z]=(dq+rc,path+[arg]);changed=True
    rcmin=iv.mpf(D[tgt][0]);print('  group order',len(D),'path to target',D[tgt][1],'rc*W',float(D[tgt][0]*WW))
    lb=rcmin+sum(B[c]*iv.mpf(y[c].a) for c in caps)+sum(N[w]*piv[j] for j,w in enumerate(W))   # y_c taken at lower end: exact feasibility
    paidm=sum(iv.mpf(n*NC*r_)/(m*WW)*iv.exp(ai*iv.log(iv.mpf(m)/r_)) for r_,n in paid.items())
    M=paidm+lb
    return M,-r.fun/S
for astr in sys.argv[1:]:
    M,lpv=certify(astr);print(astr,'certified moment lower bound',mp.nstr(M.a,25),'>=1:',M.a>=1)
