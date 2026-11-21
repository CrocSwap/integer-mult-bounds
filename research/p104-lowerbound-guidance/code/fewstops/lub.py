# L/U causal bounds per gate (fixed gate order); per-register minimal stays lower bound (greedy segmentation).
from ls import *
from reassign import basis_of
from collections import Counter
setup(W)
def join(a,b):
    if a&b==b: return a
    if a&b==a: return b
    S=set(v for v in range(512) if a>>v&1)
    for v in range(512):
        if b>>v&1 and v not in S: S|={x^v for x in S}
    m=0
    for v in S: m|=1<<v
    return m
init=[SM_[x] for x in W['initial']]; fin=[SM_[x] for x in W['final']]
def bounds(P2):
    L=[None]*len(P2); U=[None]*len(P2)
    cl=list(init)
    for i,e in enumerate(P2):
        if e[0] in('ADD','COPY'):
            d,s_=e[1],e[2]
            if d<n and s_<n: g=join(cl[d],cl[s_]); cl[d]=cl[s_]=g; L[i]=g
            elif d<n or s_<n:
                r=d if d<n else s_; cl[r]=SM_[e[4]]; L[i]=SM_[e[4]]
        elif e[0]=='SCALE' and e[1]<n: L[i]=cl[e[1]]
    cu=list(fin)
    for i in range(len(P2)-1,-1,-1):
        e=P2[i]
        if e[0] in('ADD','COPY'):
            d,s_=e[1],e[2]
            if d<n and s_<n: g=cu[d]&cu[s_]; cu[d]=cu[s_]=g; U[i]=g
            elif d<n or s_<n:
                r=d if d<n else s_; cu[r]=SM_[e[4]]; U[i]=SM_[e[4]]
        elif e[0]=='SCALE' and e[1]<n: U[i]=cu[e[1]]
    return L,U
if __name__=='__main__':
    L,U=bounds(P)
    assert all(L[i]&U[i]==L[i] for i in range(len(P)) if L[i] is not None)
    seq={r:[] for r in range(n)}
    for i,e in enumerate(P):
        if e[0] in('ADD','COPY'):
            for r in (e[1],e[2]):
                if r<n: seq[r].append(i)
        elif e[0]=='SCALE' and e[1]<n: seq[e[1]].append(i)
    st=stays_of(W)
    tot=Counter(); lb=Counter(); exact=Counter()
    for r in range(n):
        # greedy: segments of consecutive gates with join(L) subset meet(U); include init as lower, fin as upper
        segs=0; jl=None; mu=None
        for i in seq[r]:
            if jl is None: jl,mu=L[i],U[i]; segs=1; continue
            j2=join(jl,L[i]); m2=mu&U[i]
            if j2&m2==j2: jl,mu=j2,m2
            else: segs+=1; jl,mu=L[i],U[i]
        k=kind(r); kk='M' if k!='H' else 'H'
        # stays counting init/final as stays if distinct: compare #distinct charts incl endpoints is messy; compare #stays
        tot[kk]+=len(st[r]); lb[kk]+=segs; exact[(kk,len(st[r])==segs)]+=1
    print('actual stays',dict(tot),'greedy LB stays (fixed order)',dict(lb)); print(sorted(exact.items()))
