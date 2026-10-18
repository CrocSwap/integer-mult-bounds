"""(C) clique-averaging: for a support R, omega = clique number of the non-orthogonality graph, and per-line counts of omega-cliques.
If every line lies in the same number of omega-cliques then f(s) >= s|R|/omega for every s (proof in THEORY §7)."""
import sys; sys.path.insert(0,'.')
from ptlib import *
from collections import Counter
def cl(R,k):
    out=[]
    def ext(cur,cand):
        if len(cur)==k: out.append(cur); return
        for i,c in enumerate(cand): ext(cur+[c],[d for d in cand[i+1:] if G[c,d]!=0])
    ext([],R); return out
def report(name,R):
    w=max(k for k in range(1,10) if cl(R,k))
    C=cl(R,w); cnt=Counter(t for c in C for t in c)
    print(name,'|R|',len(R),'omega',w,'#omega-cliques',len(C),'per-line counts',sorted(set(cnt[t] for t in R)),'uncovered',sum(1 for t in R if cnt[t]==0),flush=True)
# P112 coordinate support: frame F0 dead, f in frame, R = live lines non-orth to f
fr=[0]
for i in range(NL):
    if len(fr)<8 and i not in fr and all(G[i,j]==0 for j in fr): fr.append(i)
f=fr[0]; R=[t for t in range(NL) if t not in fr and G[t,f]!=0]
report('P112 coordinate support N(f)-frame',R)
# E7 (c3): E7 = a^perp, f in a 7-frame of E7, R = N(f) cap E7 minus f
a=0; E7=ORTH[a]; fr7=[E7[0]]
for t in E7:
    if len(fr7)<7 and all(G[t,j]==0 for j in fr7) and t not in fr7: fr7.append(t)
f=fr7[0]; R7=[t for t in E7 if t not in fr7 and G[t,f]!=0]
report('E7-minus-frame support',R7)
R8=[t for t in range(NL) if G[t,0]!=0]
report('E8 root support N(0)',R8)
