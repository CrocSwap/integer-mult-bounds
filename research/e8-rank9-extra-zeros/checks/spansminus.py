# ZPIN2 spansminus.py: exact span facts (S1-), (S2-), (C-A) on E8 (integer roots; rank mod p is a lower bound for the rational rank, upper bounds are trivial).
import sys, itertools
from blib import *
p=2**61-1
def rank(rows):
    M=[[x%p for x in r] for r in rows]; rk=0; ncol=8
    for c in range(ncol):
        piv=next((i for i in range(rk,len(M)) if M[i][c]),None)
        if piv is None: continue
        M[rk],M[piv]=M[piv],M[rk]; inv=pow(M[rk][c],p-2,p)
        M[rk]=[x*inv%p for x in M[rk]]
        for i in range(len(M)):
            if i!=rk and M[i][c]:
                f=M[i][c]; M[i]=[(a-f*b)%p for a,b in zip(M[i],M[rk])]
        rk+=1
    return rk
R=[[int(2*x) for x in E[u]] for u in range(N)]
assert all(2*x==int(2*x) for u in range(N) for x in E[u])
# (S1-): r(O_u \ {s0}) spans r_u^perp (rank 7) for all u, s0
bad1=sum(1 for u in range(N) for s0 in O[u] if rank([R[s] for s in O[u] if s!=s0])!=7)
print('(S1-) failures:',bad1,' (checked',sum(len(O[u]) for u in range(N)),'cases)')
# (S2-): r(O_u ∩ O_u' \ {s0}) spans <r_u,r_u'>^perp (rank 6) for all u != u', s0 (s0 = none included)
bad2=0; cases=0
for u,w in itertools.combinations(range(N),2):
    C=sorted(O[u]&O[w])
    for s0 in [None]+C:
        cases+=1
        if rank([R[s] for s in C if s!=s0])!=6: bad2+=1
print('(S2-) failures:',bad2,' (checked',cases,'cases)')
# (C-A): F = frames()[0]; for every pair {a,b} ⊆ F and every s0 ∉ F: r(O_s0 \ Lambda_ab) spans r_s0^perp, Lambda_ab = lines of the 3 F-tetrads through {a,b}
F=frames()[0]; TT=tetrads(F); badA=0; c=0
for a,b in itertools.combinations(F,2):
    Lam={u for T,Ls in TT.items() if a in T and b in T for u in Ls}; assert len(Lam)==24
    for s0 in range(N):
        if s0 in F: continue
        c+=1
        if rank([R[s] for s in O[s0] if s not in Lam])!=7: badA+=1
print('(C-A) failures:',badA,' (checked',c,'cases, all 28 pairs of frames()[0])')
