# optimistic per-register relaxed chains (DAG reorder, per register independent): kappa upper estimate
import sys; sys.path.insert(0,'../fewstops'); import os; os.chdir('../fewstops')
from dagb import *
from lub import join
import itertools
init=[SM_[x] for x in W['initial']]; fin=[SM_[x] for x in W['final']]
Pnew=Counter(); Pold=Counter()
st=stays_of(W)
fb=0
for r in range(n):
    ch=[init[r]]+[c for c,_,_ in st[r]]+[fin[r]]
    for a,b in zip(ch,ch[1:]):
        if a!=b: Pold[dm(b)-dm(a)]+=1
    segs=[]; jl=None; mu=None
    for B in [sum(blocks.get(r,[]),[])]:
        ev=sorted([i for i in B if L[i] is not None],key=lambda i:(dm(L[i]),-dm(U[i])))
        for i in ev:
            if jl is None: jl,mu=L[i],U[i]; continue
            j2=join(jl,L[i]); m2=mu&U[i]
            if j2&m2==j2: jl,mu=j2,m2
            else: segs.append((jl,mu)); jl,mu=L[i],U[i]
    if jl is not None: segs.append((jl,mu))
    # choose chart per segment by DP over {jl, mu-dims}: concave -> pick lowest or highest feasible; use dims only (optimistic)
    dims=[dm(init[r])]
    for a,b in segs: dims.append((dm(a),dm(b)))
    # DP over choice lo/hi with monotone dims
    best={dm(init[r]):0.0}; path={dm(init[r]):[]}
    for lo,hi in dims[1:]:
        nb={}; npth={}
        for d0,c0 in best.items():
            for d in {max(lo,d0),hi} if hi>=d0 else set():
                if d<lo or d>hi: continue
                c=c0+f(d-d0)
                if d not in nb or c<nb[d]: nb[d]=c; npth[d]=path[d0]+[d]
        best,path=nb,npth
        if not best: break
    dfin=dm(fin[r]); bc=None
    for d0,c0 in best.items():
        if d0<=dfin:
            c=c0+f(dfin-d0)
            if bc is None or c<bc[0]: bc=(c,path[d0]+[dfin])
    if bc is None:
        seq=[dm(x) for x in ch]; fb+=1
    else: seq=[dm(init[r])]+bc[1]
    for a,b in zip(seq,seq[1:]):
        if b>a: Pnew[b-a]+=1
nat=pk.native_from_word(W); P0=Counter(nat['P'])
for k,v in Pold.items(): P0[k]-=v
for k,v in Pnew.items(): P0[k]+=v
ci=pk.caller_invoice(C); inv=pk.invoice(ci,dict(nat,P=P0))
print('fallbacks',fb); print('public moves old',sum(Pold.values()),'relaxed',sum(Pnew.values()))
print('ORDER-FREE per-register (YFIRST ceiling, DAG L/U fixed) kappa',str(pk.kappa(inv['T'],inv['P'],20)['lo'])[:16])
