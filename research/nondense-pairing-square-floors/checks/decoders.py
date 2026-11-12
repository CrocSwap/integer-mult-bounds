import sys, itertools
from lib import e8_roots, lines, dot, rank2 as rank_f2
from fractions import Fraction as F
L=lines(e8_roots()); N=len(L)
G=[[int(dot(a,b)) for b in L] for a in L]
F0=[i for i in range(N) if all(L[i][k]==0 or True for k in range(8))]
# P104 cost-56 decoder (exact rebuild of the frame-pair decoder of #968 with our dense B).  coordinate frame: e_{2a}±e_{2a+1}
def idx(v): return L.index(v) if v in L else L.index(tuple(-x for x in v))
def vec(*p):
    r=[F(0)]*8
    for i,s in p: r[i]=F(s)
    return tuple(r)
F0=[idx(vec((2*a,1),(2*a+1,1))) for a in range(4)]+[idx(vec((2*a,1),(2*a+1,-1))) for a in range(4)]
assert all(G[a][b]==0 for a in F0 for b in F0 if a!=b)
pool=[i for i in range(N) if i not in F0]
frames=[]
def rec(cur,cand):
    if len(cur)==8: frames.append(tuple(cur)); return
    for j in cand:
        rec(cur+[j],[k for k in cand if k>j and G[j][k]==0])
rec([],pool)
print("frames",len(frames))
def sols(F1):
    out=[]
    for sm in range(256):
        S=[F0[j] for j in range(8) if sm>>j&1]; need=8-len(S)
        part={f:[g for g in F1 if [x for x in S if G[g][x]]==[f]] for f in S}
        if any(not v for v in part.values()): continue
        for ch in itertools.product(*[part[f] for f in S]):
            if len(set(ch))!=len(S): continue
            Ts=[g for g in F1 if g not in ch]
            if len(Ts)!=need: continue
            rest=[f for f in F0 if f not in S]
            p2={g:[f for f in rest if [x for x in Ts if G[f][x]]==[g]] for g in Ts}
            if any(not v for v in p2.values()): continue
            for ch2 in itertools.product(*[p2[g] for g in Ts]):
                if len(set(ch2))!=len(Ts): continue
                out.append(list(zip(S,ch))+list(zip(Ts,ch2)))
    return out
def cost(A,Bc,dead):
    live=[t for t in range(N) if t not in dead]; rs=[]
    for a,b in zip(A,Bc):
        R=[t for t in live if dot(L[t],a)!=0]; C=[t for t in live if dot(L[t],b)!=0]
        rs.append(rank_f2([sum(1<<i for i,s in enumerate(C) if s==t or G[t][s]==0) for t in R]))
    return rs,live
n=0
for F1 in frames:
    s=sols(F1)
    if s:
        n+=1
        if n==1:
            ex=(F1,s)
print("admissible",n)
F1,s=ex; pairs=s[0]; print("F1",F1,"nsols",len(s))
A=[L[a] for a,b in pairs]; Bc=[tuple(2*G[a][b]*x for x in L[b]) for a,b in pairs]
# exactness: Gram on live
dead=set(F0)|set(F1); rs,live=cost(A,Bc,dead)
ok=all(sum(dot(L[t],A[k])*dot(L[s_],Bc[k]) for k in range(8))==2*G[t][s_]  for t in live for s_ in live)
print("exact D T^T=2G on",len(live),ok,"ranks",rs,"sum",sum(rs))
print("a_k in F0?",[a in F0 for a,b in pairs]," b partner in F1?",[b in F1 for a,b in pairs])
print("a.b odd diag:",[G[a][b] for a,b in pairs])
al=[a for a,b in pairs]; be=[b for a,b in pairs]

# --- checks asserted by verify.sh
F0s,F1s=set(F0),set(F1)
orth8=lambda F:all(G[a][c]==0 for a in F for c in F if a!=c) and len(set(F))==8
dead_ok=orth8(F0) and orth8(F1) and not (F0s&F1s) and len(F0s|F1s)==16 and len(live)==104
print("P104 dead lines = two disjoint orthogonal 8-frames:",dead_ok,"| exact:",ok,"| per-term dense ranks",rs,"sum",sum(rs))
print("PASS P104 cost 56 decoder: exact on 104 live lines, 8 terms of rank 7" if (dead_ok and ok and rs==[7]*8) else "FAIL P104")
# --- E8 (coordinate) and P112 (live frame) square decoders: exact Gram and per-term dense rank
def term_ranks(X,Y,live):
    out=[]
    for x,y in zip(X,Y):
        R=[t for t in live if dot(L[t],x)!=0]; C=[t for t in live if dot(L[t],y)!=0]
        out.append(rank_f2([sum(1<<i for i,s in enumerate(C) if s==t or G[t][s]==0) for t in R]))
    return out
E=[tuple(F(int(i==j)) for i in range(8)) for j in range(8)]
allL=list(range(N))
okE=all(sum(dot(L[t],e)*dot(L[s_],e) for e in E)==G[t][s_] for t in allL for s_ in allL)
rE=term_ranks(E,E,allL); print("E8 coordinate decoder X=Y=I (T=8): exact Gram",okE,"term ranks",rE,"cost",sum(rE))
print("PASS E8 coordinate decoder: cost 72 = 8 x 9" if okE and rE==[9]*8 else "FAIL E8")
Fr=[L[i] for i in F0]   # live set = E8 minus the frame F0 (112 lines); decoder x_j=y_j=frame line, scaled 1/2
live112=[t for t in range(N) if t not in F0s]
okP=all(sum(dot(L[t],f)*dot(L[s_],f) for f in Fr)==2*G[t][s_] for t in live112 for s_ in live112)
rP=term_ranks(Fr,Fr,live112); print("P112 frame decoder x_j=y_j=F0 line (T=8): D T^T = 2G exactly",okP,"term ranks",rP,"cost",sum(rP))
print("PASS P112 live-frame decoder: cost 64 = 8 x 8" if okP and rP==[8]*8 else "FAIL P112")
sys.exit(0 if (dead_ok and ok and rs==[7]*8 and okE and rE==[9]*8 and okP and rP==[8]*8) else 1)
