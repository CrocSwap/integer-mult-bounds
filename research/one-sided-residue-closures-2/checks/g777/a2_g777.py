# AUDIT-IQ independent check of G777 two-7-flat leftover facts. Own E8 build (numpy), labels (1, r mod 2E8),
# 7-flats as common kernels of 2-dim dual subspaces, leftover enumeration by size-pruned pair search.
import numpy as np, itertools, sys, pickle, json, csv
from collections import Counter
R=[]
for i,j in itertools.combinations(range(8),2):
    for a in (2,-2):
        for b in (2,-2):
            v=[0]*8; v[i]=a; v[j]=b; R.append(v)
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(list(s))
def canon(v):
    for x in v:
        if x: return tuple(v) if x>0 else tuple(-y for y in v)
L=np.array(sorted({canon(r) for r in R})); n=len(L); G=(L@L.T)//4
S=np.array([[1,-1,-1,-1,-1,-1,-1,1],[2,2,0,0,0,0,0,0],[-2,2,0,0,0,0,0,0],[0,-2,2,0,0,0,0,0],[0,0,-2,2,0,0,0,0],[0,0,0,-2,2,0,0,0],[0,0,0,0,-2,2,0,0],[0,0,0,0,0,-2,2,0]])
Cc=np.rint(L@np.linalg.inv(S)).astype(int); assert (Cc@S==L).all()      # simple-root coordinates
lab=[256|int(sum((int(c)%2)<<k for k,c in enumerate(row))) for row in Cc]
assert len(set(lab))==120
pc=lambda x: x.bit_count()
par=lambda x: x.bit_count()&1
# all 7-dim subspaces = kernels of 2-dim dual subspaces {a,b,a^b}
seen=set(); F7=[]
for a in range(1,512):
    for b in range(a+1,512):
        key=tuple(sorted((a,b,a^b)))
        if key in seen: continue
        seen.add(key); F7.append(sum(1<<t for t in range(n) if not par(a&lab[t]) and not par(b&lab[t])))
print('7-dim subspaces',len(seen),'max lines in a 7-flat',max(map(pc,F7)),flush=True)
F7=sorted(set(F7))
def best2(T,need=None):
    A=sorted({m&T for m in F7},key=pc,reverse=True); sz=[pc(x) for x in A]; best=0
    for i in range(len(A)):
        if sz[i]+sz[0]<=best: break
        for j in range(i,len(A)):
            if sz[i]+sz[j]<=best: break
            u=A[i]|A[j]
            if need is not None and not u>>need&1: continue
            best=max(best,pc(u))
    return best
full=(1<<n)-1
def off_J(J):  # lines NOT in span of simple roots J  (coords outside J nonzero)
    return sum(1<<t for t in range(n) if any(Cc[t][i]!=0 for i in range(8) if i not in J))
# (a) non-root h: maximal non-E7 parabolics + all 6-subsets of E7 nodes {0..6} (node 7 = Bourbaki a8)
out={}
for J in [tuple(x for x in range(8) if x!=j) for j in range(7)]+[tuple(x for x in range(7) if x!=j) for j in range(7)]:
    T=off_J(J); b=best2(T); out[J]=(pc(T),pc(T)-b); print('J',J,'|Off|',pc(T),'minleft',pc(T)-b,flush=True)
print('NONROOT min leftover',min(v[1] for v in out.values()),flush=True)
# (b) root r0 (line 0): leftovers with r0 covered, size <= 16
def leftovers(ri,K):
    T=sum(1<<t for t in range(n) if G[ri][t]!=0)
    A=sorted({m&T for m in F7},key=pc,reverse=True); sz=[pc(x) for x in A]; need=pc(T)-K; Ls=set()
    for i in range(len(A)):
        if sz[i]+sz[0]<need: break
        for j in range(i,len(A)):
            if sz[i]+sz[j]<need: break
            u=A[i]|A[j]
            if u>>ri&1 and pc(u)>=need: Ls.add(T&~u)
    Ls=sorted(Ls,key=pc); mins=[]
    for e in Ls:
        if not any(f&e==f for f in mins): mins.append(e)
    return T,mins
T0,mins=leftovers(0,16)
print('r0 |Off|',pc(T0),'min leftover sizes',sorted(Counter(map(pc,mins)).items()),flush=True)
bits=lambda m:[t for t in range(n) if m>>t&1]
def f2rank(vs):
    b=[]
    for x in vs:
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return len(b)
print('label ranks',sorted(Counter((pc(e),f2rank([lab[t] for t in bits(e)])) for e in mins).items()),flush=True)
Qs=[e for e in mins if pc(e)==8]; Ms=[e for e in mins if pc(e)==12]
# Q structure: full 4-flat, real span dim 4, lines in real span = D4 (12), Q = D4 minus 4 mutually orthogonal lines
okQ=0
for q in Qs:
    B=bits(q); span=[x for x in range(512)]  # label span
    sp={0}
    for t in B: sp|={x^lab[t] for x in sp}
    full4=(len(sp)==16 and sum(1 for t in range(n) if lab[t] in sp)==8)
    rk=np.linalg.matrix_rank(L[B].astype(float))
    P=np.linalg.pinv(L[B].astype(float).T)
    inspan=[t for t in range(n) if np.allclose(L[B].astype(float).T@(P@L[t]),L[t])]
    rest=[t for t in inspan if t not in B]
    frame=len(rest)==4 and all(G[a][b]==0 for a in rest for b in rest if a!=b)
    okQ+= full4 and rk==4 and len(inspan)==12 and frame
print('Q count',len(Qs),'all full-4-flat & D4-minus-frame',okQ==len(Qs),flush=True)
print('r0 in any leftover?',any(m&1 for m in mins))
# N_Q for one Q: roots r (r covered) having Q as a minimal leftover
def is_minleft(ri,q):
    T=sum(1<<t for t in range(n) if G[ri][t]!=0)
    if q&~T: return False
    A=sorted({m&T for m in F7 if not m&q},key=pc,reverse=True); need=T&~q
    for i in range(len(A)):
        if pc(A[i])+pc(A[0])<pc(need): break
        for j in range(i,len(A)):
            u=A[i]|A[j]
            if u==need and u>>ri&1: return True
    return False
# (exact leftover == q is enough: q minimal among r0's, minimality for other r follows from W-equivariance)
q=Qs[0]; NQ=[r for r in range(n) if is_minleft(r,q)]
print('N_Q for Q0',len(NQ),NQ,'roots inside Q0',[r for r in NQ if q>>r&1],flush=True)
pickle.dump((lab,T0,mins),open('a2_left.pkl','wb'))
