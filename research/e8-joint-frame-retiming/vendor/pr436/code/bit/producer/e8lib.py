"""Dylan Crow, with Anthropic Claude assistance; Apache-2.0. E8 root lines in Q^8 (standard coordinates, doubled to integers), F2 images, basic linear algebra."""
import itertools
from fractions import Fraction as Fr

def roots2():
    """E8 roots times 2 (integer vectors): 2(±e_i±e_j) and (±1)^8 with even number of minus signs."""
    R=[]
    for i,j in itertools.combinations(range(8),2):
        for a in (2,-2):
            for b in (2,-2):
                v=[0]*8; v[i]=a; v[j]=b; R.append(tuple(v))
    for signs in itertools.product((1,-1),repeat=8):
        if signs.count(-1)%2==0: R.append(tuple(signs))
    return R

def ip(u,v):  # true inner product of roots given doubled coordinates
    return sum(a*b for a,b in zip(u,v))//4

import os
def roots_hamming():
    """E8 via Construction A from the [8,4,4] extended Hamming code: x in Z^8, x mod 2 in H8, |x|^2=4.
    Inner product of roots = <x,y>/2. Returned scaled so that ip() (which divides by 4) works: multiply by sqrt2? no:
    we return 2*x/sqrt... -> use integer vectors y=x and a separate scale."""
    H=[]
    for a in itertools.product((0,1),repeat=4):
        g=[(1,1,1,1,0,0,0,0),(1,1,0,0,1,1,0,0),(1,0,1,0,1,0,1,0),(0,1,1,0,1,0,0,1)]
        w=[sum(a[k]*g[k][i] for k in range(4))%2 for i in range(8)]
        H.append(tuple(w))
    R=[]
    for i in range(8):
        for sg in (2,-2):
            v=[0]*8; v[i]=sg; R.append(tuple(v))
    for w in H:
        if sum(w)==4:
            idx=[i for i in range(8) if w[i]]
            for sg in itertools.product((1,-1),repeat=4):
                v=[0]*8
                for i,s_ in zip(idx,sg): v[i]=s_
                R.append(tuple(v))
    return R
COORD=os.environ.get('E8COORD','std')
if COORD=='ham':
    ALL=[tuple(a for a in r) for r in roots_hamming()]
    def ip(u,v): return sum(a*b for a,b in zip(u,v))//2
else:
    ALL=roots2()
assert len(ALL)==240
LINES=[]
seen=set()
for r in ALL:
    if r in seen: continue
    neg=tuple(-a for a in r); seen.add(r); seen.add(neg)
    # canonical: first nonzero coordinate positive
    LINES.append(r if [a for a in r if a][0]>0 else neg)
V=len(LINES); assert V==120
G=[[ip(LINES[a],LINES[b]) for b in range(V)] for a in range(V)]
ORTH=[[b for b in range(V) if G[a][b]==0] for a in range(V)]
NEIGH=[[b for b in range(V) if abs(G[a][b])==1] for a in range(V)]
assert all(len(o)==63 and len(n)==56 for o,n in zip(ORTH,NEIGH))

def rank_q(vecs):
    """rank over Q of integer vectors"""
    rows=[list(map(Fr,v)) for v in vecs]
    r=0; n=len(rows[0]) if rows else 0
    for c in range(n):
        p=None
        for i in range(r,len(rows)):
            if rows[i][c]!=0: p=i;break
        if p is None: continue
        rows[r],rows[p]=rows[p],rows[r]
        for i in range(len(rows)):
            if i!=r and rows[i][c]!=0:
                f=rows[i][c]/rows[r][c]
                rows[i]=[x-f*y for x,y in zip(rows[i],rows[r])]
        r+=1
    return r

def span_dim(idx):
    return rank_q([LINES[i] for i in idx]) if idx else 0
