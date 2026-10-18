# ZPIN2 rigA2.py: exact finite checks for Theorem Z and Theorem U on L' = E8 \ S, S an A2 triangle (integer arithmetic on E8 roots, blib).
import sys, itertools
from blib import *
nn=G[0][0]
def line_of(vec):
    for k in range(N):
        if all(a==b for a,b in zip(vec,E[k])) or all(a==-b for a,b in zip(vec,E[k])): return k
    return None
def triangle(i,j):
    s=1 if G[i][j]>0 else -1
    k=line_of([a-s*b for a,b in zip(E[i],E[j])]); return (i,j,k)
j=[j for j in range(1,N) if G[0][j]!=0][0]
S=triangle(0,j); assert all(G[a][b]!=0 for a,b in itertools.combinations(S,2)) and len(set(S))==3
Lp=[u for u in range(N) if u not in S]; Lps=set(Lp)
print('S =',S,'|L\'| =',len(Lp))
allF=frames()
print('frames of E8:',len(allF))
def miss_ok(F,missing):  # every F-tetrad misses <=1 line of 'missing' (lines of F itself are not tetrad lines)
    TT=tetrads(F); cnt={}
    for m in missing:
        if m in F: continue
        k=frozenset(f for f in F if G[m][f]!=0); cnt[k]=cnt.get(k,0)+1
    return max(cnt.values(),default=0)<=1
# (HU) coordinate frame for Theorem U (UNIQ8 hypothesis H; F0 lines may be missing)
HU=[F for F in allF if miss_ok(F,S)]
print('(HU) coordinate frames with H for L\':',len(HU))
# H-frames inside L'
Hfr=[F for F in allF if not (set(F)&set(S)) and miss_ok(F,S)]
print('frames inside L\':',sum(1 for F in allF if not set(F)&set(S)),' H-frames inside L\':',len(Hfr))
byl={}
for F in Hfr:
    for f in F: byl.setdefault(f,[]).append(F)
print('(C1) every line of L\' in an H-frame:',all(u in byl for u in Lp),' min count',min(len(byl.get(u,[])) for u in Lp))
def refl(v,g):
    c=2*G[v][g]//G[g][g]; assert 2*G[v][g]%G[g][g]==0
    return line_of([a-c*b for a,b in zip(E[v],E[g])])
def c2(v,g):
    sv=refl(v,g)
    for F in byl.get(g,[]):
        T=frozenset(f for f in F if G[v][f]!=0)
        other=[t for t in range(N) if t not in F and frozenset(f for f in F if G[t][f]!=0)==T and t!=v and G[t][v]!=0]
        assert len(other)==4 and sv in other
        if all(t in Lps for t in other if t!=sv): return True
    return False
non=[(v,g) for v in Lp for g in Lp if v!=g and G[v][g]!=0]
bad=[p for p in non if not c2(*p)]
print("(C2'') ordered non-orth pairs in L':",len(non),' failing:',len(bad))
