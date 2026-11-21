#!/usr/bin/env python3
"""NOGAIN lwcx.py (own code). Exact test of LEVEL-WALL on a real legal network (Q96 and P104).
Network (routed E8 decoder): n gatherers g_t (a=<q_t>, b=0, F=e_t) -> 8 hubs (a=<v_h,w_h>, b=<v_h>), H[h,t]=U[t,h], G[:,h]=W[:,h].
Computes YC level sum (sources dim a>=l, sinks dim b<l) and the downward-crossing sum DX (walks with some a>=l before some b<l)."""
import json, itertools, numpy as np
from fractions import Fraction as Fr
WD='<research-tree>/cards/WILD/'
G=np.load(WD+'REBASET1/G104.npy').astype(int); L=json.load(open(WD+'REBASET1/lines104.json'))
dot=lambda a,b: bin(a&b).count('1')&1
F0=[0,6,16,22,29,36,45,95]; Ah=G[:,F0]
def f2basis(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return b
def rankQ(rows):  # exact rank over Q, rows = list of lists of Fractions
    M=[list(r) for r in rows]; r=0; ncol=len(M[0]) if M else 0
    for c in range(ncol):
        p=next((i for i in range(r,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]; pv=M[r][c]
        for i in range(len(M)):
            if i!=r and M[i][c]!=0:
                f=M[i][c]/pv; M[i]=[x-f*y for x,y in zip(M[i],M[r])]
        r+=1
    return r
# kernel-type lines: alpha with label span of D(alpha) a hyperplane (computed over the 104 ports)
cand=[]
for a in itertools.product(range(-2,3),repeat=8):
    if not any(a): continue
    if next(x for x in a if x)<0: continue
    D=np.nonzero(Ah@np.array(a))[0]
    bs=f2basis([L[t] for t in D])
    if len(bs)==8:
        v=[x for x in range(1,512) if all(dot(x,y)==0 for y in bs)]; cand.append((a,v[0]))
print('candidate hyperplane-deposit alphas:',len(cand))
chosen=[]
for a,v in cand:
    T=[list(c[0]) for c in chosen]+[list(a)]
    if rankQ([[Fr(x) for x in r] for r in T])==len(T): chosen.append((a,v))
    if len(chosen)==8: break
assert len(chosen)==8
A=np.array([c[0] for c in chosen]).T
Ainv=[[Fr(x) for x in r] for r in np.round(np.linalg.inv(A)*abs(round(np.linalg.det(A)))).astype(int).tolist()]
det=Fr(round(np.linalg.det(A)))
Ainv=[[x/abs(det) for x in r] for r in Ainv]
for n in (96,104):
    Ahn=Ah[:n]
    W=[[Fr(int(x)) for x in r] for r in (Ahn@A).tolist()]                       # n x 8
    AinvT=[[Ainv[j][i] for j in range(8)] for i in range(8)]
    U=[[sum(Fr(int(Ahn[t][k]))*AinvT[k][h] for k in range(8))/4 for h in range(8)] for t in range(n)]
    M=[[sum(W[s][h]*U[t][h] for h in range(8)) for t in range(n)] for s in range(n)]
    dec=all(M[t][t]==1 for t in range(n)) and all(M[s][t]==0 for s in range(n) for t in range(n) if s!=t and dot(L[s],L[t]))
    dep=all(dot(L[s],chosen[h][1])==0 for h in range(8) for s in range(n) if W[s][h]!=0)
    # nodes: (dim a, dim b); gatherers 0..n-1, hubs n..n+7. walks: g_t -> h (length 2) only (gatherers do not deposit)
    nodes=[(1,0)]*n+[(2,1)]*8
    D=sum(a-b for a,b in nodes)
    yc=0; dx=0; per=[]
    for l in range(1,10):
        # YC: walk g_t->h counted iff dim a(g_t)>=l and dim b(h)<l
        Myc=[[W[s][h]*U[t][h] if (1>=l and 1<l) else 0 for t in range(n)] for s in range(n) for h in [0]]  # always 0 (1>=l>1 impossible)
        ryc=0
        # DX: counted iff exists i<=j on walk [g_t,h] with a_i>=l>b_j
        seq=[(1,0),(2,1)]
        cross=any(seq[i][0]>=l>seq[j][1] for i in range(2) for j in range(i,2))
        rdx=rankQ(M) if cross else 0
        yc+=ryc; dx+=rdx; per.append((l,ryc,rdx))
    print(f'n={n}: decoder conds {dec}; deposit rule {dep}; rank M {rankQ(M)}; D={D}; YC level sum={yc}; DX sum={dx}; per-level (l,YC,DX)={per}')
