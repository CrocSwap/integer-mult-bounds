"""MERGEROWS m2: cost-safe refactorization (row transvections) + 2-power gauge climb of alpha+beta.
Move T(k->k',c): w_k' += c w_k, u_k -= c u_k'.  Exact decoder preserved.  Accepted only if total cost does not rise.
Valid floor: C(orig) >= C(new) >= alpha+beta(new)."""
import sys, pickle, numpy as np
from fractions import Fraction as Fr
sys.path.insert(0,'../iso3')
from gmax import *
def prices(rows,Q):
    n=len(Q); out=[]
    for w,u in rows:
        D=[t for t in range(n) if w[t]!=0]; S=[t for t in range(n) if u[t]!=0]
        out.append(rk2(Q[np.ix_(D,S)]) if D and S else 0)
    return out
def transvect(rows,k,kp,c):
    w,u=rows[k]; wp,up=rows[kp]
    new=list(rows); new[kp]=([a+c*b for a,b in zip(wp,w)],up); new[k]=(w,[a-c*b for a,b in zip(u,up)])
    return new
def clean(rows): return [(w,u) for w,u in rows if any(w) and any(u)]
def search(rows,Q,iters=60,seed=0,gi=250,coefs=(1,-1,2,-2,Fr(1,2),Fr(-1,2),3,-3)):
    rng=np.random.default_rng(seed); C0=sum(prices(rows,Q))
    best=gauge_max(rows,Q,gi,seed)['gmax_sum']; cur=rows; bestrows=rows; hist=[best]
    for it in range(iters):
        m=len(cur); k,kp=rng.choice(m,2,replace=False); c=coefs[rng.integers(len(coefs))]
        new=clean(transvect(cur,k,kp,Fr(c)))
        if sum(prices(new,Q))>C0: continue
        g=gauge_max(new,Q,gi,int(rng.integers(1<<30)))['gmax_sum']
        if g>=best-1: cur=new
        if g>best: best=g; bestrows=new; hist.append(g)
    return C0,best,bestrows,hist
def safe_pairs(rows,Q):
    m=len(rows); pr=prices(rows,Q); ok=[]
    for k in range(m):
        for kp in range(m):
            if k!=kp and sum(prices(transvect(rows,k,kp,Fr(1)),Q))<=sum(pr): ok.append((k,kp))
    return ok
if __name__=='__main__':
    f,setn=sys.argv[1],sys.argv[2]; iters=int(sys.argv[3]) if len(sys.argv)>3 else 60
    rows=pickle.load(open(f,'rb')); L=std_set(setn); Q=Q_std(L); assert check_decoder(rows,Q)==0
    pr=prices(rows,Q); print(f,'rankQ',rk2(Q),'prices',pr,'C',sum(pr)); sp=safe_pairs(rows,Q); print('cost-safe pairs',len(sp),'of',len(rows)*(len(rows)-1))
    C0,best,br,hist=search(rows,Q,iters,0)
    assert check_decoder(br,Q)==0
    print('RESULT C0',C0,'C_new',sum(prices(br,Q)),'S1 best',best,'hist',hist,flush=True)
    pickle.dump(br,open('best_'+f.split('/')[-1],'wb'))
def safe_any(rows,Q,k,kp,C0=None):
    """all coefficients c (generic + every cancelling ratio) for which T(k->kp,c) keeps total cost <= C0"""
    if C0 is None: C0=sum(prices(rows,Q))
    w,u=rows[k]; wp,up=rows[kp]
    cands=set(-a/b for a,b in zip(wp,w) if a!=0 and b!=0)|set(a/b for a,b in zip(u,up) if a!=0 and b!=0)
    g=Fr(1,10007)
    while g in cands: g+=1
    out=[]
    for c in [g]+sorted(cands):
        new=clean(transvect(rows,k,kp,c))
        if sum(prices(new,Q))<=C0: out.append(c)
    return out
def rigid(rows,Q):
    C0=sum(prices(rows,Q)); m=len(rows)
    return [(k,kp,safe_any(rows,Q,k,kp,C0)) for k in range(m) for kp in range(m) if k!=kp and safe_any(rows,Q,k,kp,C0)]
