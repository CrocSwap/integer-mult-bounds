import random
from math import gcd
def prim(v):
    g=0
    for x in v: g=gcd(g,abs(x))
    if g==0: return None
    v=[x//g for x in v]
    for x in v:
        if x: return v if x>0 else [-y for y in v]
def cross(a,b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def randcfg(v, R=1, rng=random, npts=None, pfix=0.3):
    """points from a small pool in {-R..R}^3; lines through two pool points (or coordinate-ish random); p.q != 0."""
    npts = npts or max(3, v//2+1)
    pool=[]
    while len(pool)<npts:
        p=prim([rng.randint(-R,R) for _ in range(3)])
        if p and p not in pool: pool.append(p)
    P=[];Q=[]
    tries=0
    while len(P)<v and tries<10000:
        tries+=1
        p=rng.choice(pool)
        if rng.random()<pfix:
            q=prim([rng.randint(-R,R) for _ in range(3)])
        else:
            a,b=rng.sample(pool,2); q=prim(cross(a,b))
        if q and dot(p,q)!=0: P.append(p); Q.append(q)
    return P,Q
