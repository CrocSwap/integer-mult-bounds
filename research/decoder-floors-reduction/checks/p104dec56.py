"""Theorem M sharpness premise (README section 4.6): a P104 call's coordinate decoder costs 56.  Self-contained, exact (Fractions), standard library.
For the coordinate frame F0 and every frame F1 disjoint from it that admits an 8-term decoder of the pattern below, the 8 terms (a_k, b_k) with
a_k in F0 or F1 satisfy  sum_k <r_t, a_k><r_s, b_k> = 2 <r_t, r_s>  exactly on the 104 live lines (120 - F0 - F1); the cost of a term is the F2 rank of the
label pairing (<r_i, r_j> + 1 mod 2 on supports); asserted: every term has rank 7, total 56, for the first admissible F1 in lexicographic order (the build is exact and explicit; it exhibits the cost-56 decoder, which is all Theorem M's sharpness remark assumes)."""
import itertools
from fractions import Fraction as F
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def e8_roots():
    R = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                r = [F(0)] * 8; r[i] = F(si); r[j] = F(sj); R.append(tuple(r))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0: R.append(tuple(F(x, 2) for x in s))
    return R
def lines(R):
    seen = set(); L = []
    for r in R:
        if tuple(-x for x in r) in seen: continue
        seen.add(r); L.append(r)
    return L
def rank_f2(rows):
    basis = {}; r = 0
    for x in rows:
        while x:
            h = x.bit_length() - 1
            if h in basis: x ^= basis[h]
            else: basis[h] = x; r += 1; break
    return r
L=lines(e8_roots()); N=len(L)
G=[[int(dot(a,b)) for b in L] for a in L]
# coordinate frame: e_{2a}±e_{2a+1}
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
n=0; allok=True
for F1 in frames:
    s=sols(F1)
    if s:
        n+=1
        if n>1: break
        if n==1:
            ex=(F1,s)
        for pr in s[:3]:
            A_=[L[a] for a,b in pr]; B_=[tuple(2*G[a][b]*x for x in L[b]) for a,b in pr]
            rs_,lv_=cost(A_,B_,set(F0)|set(F1))
            ex_=all(sum(dot(L[t],A_[k])*dot(L[s_],B_[k]) for k in range(8))==2*G[t][s_] for t in lv_ for s_ in lv_)
            allok&=(ex_ and rs_==[7]*8 and len(lv_)==104)
print("admissible (first only)",n)
F1,s=ex; pairs=s[0]; print("F1",F1,"nsols",len(s))
A=[L[a] for a,b in pairs]; Bc=[tuple(2*G[a][b]*x for x in L[b]) for a,b in pairs]
# exactness: Gram on live
dead=set(F0)|set(F1); rs,live=cost(A,Bc,dead)
ok=all(sum(dot(L[t],A[k])*dot(L[s_],Bc[k]) for k in range(8))==2*G[t][s_]  for t in live for s_ in live)
print("exact D T^T=2G on",len(live),ok,"ranks",rs,"sum",sum(rs))
print("a_k in F0?",[a in F0 for a,b in pairs]," b partner in F1?",[b in F1 for a,b in pairs])
print("a.b odd diag:",[G[a][b] for a,b in pairs])
al=[a for a,b in pairs]; be=[b for a,b in pairs]
print("alpha Gram:",[[G[x][y] for y in al] for x in al])
print("beta Gram:",[[G[x][y] for y in be] for x in be])
print("alpha_i.beta_j:",[[G[x][y] for y in be] for x in al])
import collections
print("split sizes |S| over solutions:",collections.Counter(sum(1 for a,b in p if a in F0) for p in s))

print("all admissible (F1, solution) sampled: exact, 104 live lines, ranks 7^8, cost 56:", allok)
print("P104 coordinate decoder cost 56:", allok and sum(rs)==56 and rs==[7]*8 and ok and len(live)==104)
