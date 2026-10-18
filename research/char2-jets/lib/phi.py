"""Multiplicative char-2 realisation phi: Q* -> GF(2^16)*, -1 -> 1, prime p -> z_p (random), applied entrywise.
Preserves every BINOMIAL incidence (|pi(t) & sigma(s)| = 2): x_i y_i = -x_j y_j  ->  phi(x_i)phi(y_i) = phi(x_j)phi(y_j)."""
import random
from gr import mul, inv, EXP, LOG, Q as FQ
def factor(n):
    n=abs(n); f={}; d=2
    while d*d<=n:
        while n%d==0: f[d]=f.get(d,0)+1; n//=d
        d+=1
    if n>1: f[n]=f.get(n,0)+1
    return f
def make_phi(rng=random):
    z={}
    def phi(x):
        from fractions import Fraction
        x=Fraction(x)
        if x==0: return 0
        r=1
        for n,sgn in ((x.numerator,1),(x.denominator,-1)):
            for p,e in factor(n).items():
                if p not in z: z[p]=rng.randrange(2,FQ)
                for _ in range(e):
                    r = mul(r, z[p]) if sgn>0 else mul(r, inv(z[p]))
        return r
    return phi
def dot2(a,b): return mul(a[0],b[0])^mul(a[1],b[1])^mul(a[2],b[2])
def classify(P,Q):
    v=len(P); wild=0; H=[]
    for t in range(v):
        for s in range(v):
            if t!=s and sum(P[t][j]*Q[s][j] for j in range(3))==0:
                if all(P[t][j] and Q[s][j] for j in range(3)): wild+=1
        terms=[P[t][j]*Q[t][j] for j in range(3) if P[t][j]*Q[t][j]]
        if len(terms)==2 and abs(terms[0])==abs(terms[1]): H.append(t)
    return wild, H
