# Scalar-layer (F2) search: min #locals (then #bridges) for each pair-preserving monomial target rho.
# banks: X_p=2p, Y_p=2p+1 ; state = tuple of row bitmasks (bank i = XOR of inputs). Chain: locals alternate with bridge groups.
import sys, itertools
from collections import deque
P=int(sys.argv[1]); NB=2*P
def apply_add(st,d,s):
    l=list(st); l[d]^=l[s]; return tuple(l)
ident=tuple(1<<i for i in range(NB))
# targets: permutation of banks preserving pairing (permute pairs, optional in-pair swap)
targets={}
for perm in itertools.permutations(range(P)):
    for sw in itertools.product([0,1],repeat=P):
        t=[0]*NB
        for p in range(P):
            q=perm[p]
            for e in range(2):  # X_p -> bank
                t[2*p+e]=1<<(2*q+(e^sw[p]))
        targets[(perm,sw)]=tuple(t)
locals_=[]  # (d,s): forward Y_p+=X_p ; backward X_p+=Y_p
for p in range(P):
    locals_.append((2*p+1,2*p)); locals_.append((2*p,2*p+1))
bridges=[]
for d in range(P):
    for s in range(P):
        if d!=s: bridges.append(((2*d,2*s),(2*s+1,2*d+1)))  # X_d+=X_s ; Y_s+=Y_d
# Dijkstra-ish lexicographic over (nlocals, nbridges): BFS by nlocals layers w/ bridge closure (bridges free-cost count)
import heapq
best={}
start=(ident,-1)
pq=[(0,0,ident,-1)]
seen={}
res={}
while pq:
    nl,nb,st,last=heapq.heappop(pq)
    if (st,last) in seen: continue
    seen[(st,last)]=(nl,nb)
    for k,t in targets.items():
        if st==t and k not in res: res[k]=(nl,nb)
    if nl>=2*P+2 and len(res)==len(targets): break
    if nl>2*P+2: continue
    for (d,s) in locals_:
        p=d//2
        heapq.heappush(pq,(nl+1,nb,apply_add(st,d,s),p))
    for (a,b) in bridges:
        st2=apply_add(apply_add(st,*a),*b)
        heapq.heappush(pq,(nl,nb+1,st2,-1))
    if nb>6*(P-1)+2: pass
for k,v in sorted(res.items(),key=lambda x:x[1]):
    print(k,v)
