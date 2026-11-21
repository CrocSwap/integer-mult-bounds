# relaxed per-register stay count under any dependency-respecting reorder (indicative, per-register)
from sched import *
from collections import Counter
W0=dict(W); P0=[e for e in P if not (e[0]=='MOVE' and e[1]<n)]
setup(W)
blocks,bidx=build_blocks(P0)
init=[SM_[x] for x in W['initial']]; fin=[SM_[x] for x in W['final']]
L=[None]*len(P0)
bj={r:[None]*len(B) for r,B in blocks.items()}  # join of L over block
for i,e in enumerate(P0):
    rs=[r for r in regs_of(e) if r<n]
    if not rs: continue
    if e[0] in('ADD','COPY') and (e[1]>=n or e[2]>=n): g=SM_[e[4]]
    else:
        g=0
        for r in rs:
            b=bidx[(i,r)]
            g=join(g, bj[r][b-1] if b>0 else init[r]) if g else (bj[r][b-1] if b>0 else init[r])
    L[i]=g
    for r in rs:
        b=bidx[(i,r)]; bj[r][b]=g if bj[r][b] is None else join(bj[r][b],g)
        if b>0 and bj[r][b-1] is not None: bj[r][b]=join(bj[r][b],bj[r][b-1])
U=upper_bounds(P0)
viol=sum(1 for i in range(len(P0)) if L[i] is not None and U[i] is not None and L[i]&U[i]!=L[i])
print('L not<= U violations',viol)
tot=Counter(); lb=Counter(); lb0=Counter()
st=stays_of(W)
for r in range(n):
    segs=0; jl=None; mu=None
    for B in blocks.get(r,[]):
        ev=[i for i in B if L[i] is not None]
        ev.sort(key=lambda i:(dm(L[i]),-dm(U[i])))
        for i in ev:
            if jl is None: jl,mu=L[i],U[i]; segs=1; continue
            j2=join(jl,L[i]); m2=mu&U[i]
            if j2&m2==j2: jl,mu=j2,m2
            else: segs+=1; jl,mu=L[i],U[i]
    kk='M' if kind(r)!='H' else 'H'
    tot[kk]+=len(st[r]); lb[kk]+=segs
print('actual stays',dict(tot),'relaxed reorder count',dict(lb))
import sys
if len(sys.argv)>1:
    # registers with slack; show first few
    shown=0
    for r in range(n):
        segs=0; jl=None; mu=None
        for B in blocks.get(r,[]):
            ev=sorted([i for i in B if L[i] is not None],key=lambda i:(dm(L[i]),-dm(U[i])))
            for i in ev:
                if jl is None: jl,mu=L[i],U[i]; segs=1; continue
                j2=join(jl,L[i]); m2=mu&U[i]
                if j2&m2==j2: jl,mu=j2,m2
                else: segs+=1; jl,mu=L[i],U[i]
        if segs<len(st[r]) and kind(r)==sys.argv[1]:
            shown+=1
            if shown>3: break
            print('REG',r,kind(r),'stays',[dm(c) for c,_,_ in st[r]],'relaxed',segs)
            # map P0 index -> original stays: P0 order is P minus public moves; recompute chart of each event in original
            for bi,B in enumerate(blocks[r]):
                e0=P0[B[0]]; ro='in' if e0[0]=='ADD' and e0[1]==r else ('out' if e0[0]=='ADD' else e0[0])
                print('  block',bi,ro,len(B),'L dims',sorted(Counter(dm(L[i]) for i in B).items()),'U dims',sorted(Counter(dm(U[i]) for i in B).items()))
