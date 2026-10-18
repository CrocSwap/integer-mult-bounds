import sys
from lib import lines, dn, dot, e8_roots
from fractions import Fraction as Fr
def orth_sub(L,vs): return [r for r in L if all(dot(r,x)==0 for x in vs)]
def rank_f2(rows):
    basis=[]
    for r in rows:
        x=r
        for b in basis: x=min(x,x^b)
        if x: basis.append(x)
    return len(basis)
E8=lines(e8_roots()); r0=E8[0]; r1=next(r for r in E8 if dot(r,r0) in (1,-1))
E7=orth_sub(E8,[r0]); E6=orth_sub(E8,[r0,r1]); D5=lines(dn(5)); D4=lines(dn(4)); D6=lines(dn(6))
def Gmat(L): return [[int(dot(a,b)) for b in L] for a in L]
def B0rows(L):
    G=Gmat(L); v=len(L)
    return [sum((1<<s) for s in range(v) if s==t or G[t][s]==0) for t in range(v)]
def blk(Brows,R,A):
    return rank_f2([sum((1<<i) for i,s in enumerate(A) if Brows[t]>>s&1) for t in R])
