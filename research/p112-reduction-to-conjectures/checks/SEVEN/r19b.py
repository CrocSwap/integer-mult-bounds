# Row 19 tight case, impl B (independent): own E8 roots, D4 = E8 roots inside span(e1..e4); hyperplanes of V via integer normals;
# exact triple intersections by integer cross-product (4-dim generalized cross product = 3x3 minors).
import itertools
from fractions import Fraction
R=[]
for i,j in itertools.combinations(range(8),2):
    for s in (1,-1):
        for u in (1,-1):
            v=[0]*8; v[i]=2*s; v[j]=2*u; R.append(tuple(v))
for m in range(256):
    v=tuple(1 if m>>k&1 else -1 for k in range(8))
    if sum(1 for x in v if x<0)%2==0: R.append(v)
assert len(R)==240
lines={}
for r in R:
    k=r if r>tuple(-x for x in r) else tuple(-x for x in r); lines[k]=1
L=list(lines); assert len(L)==120
D4=[l[:4] for l in L if all(x==0 for x in l[4:])]; print('E8 lines in span(e1..e4):',len(D4))
def det3(a,b,c): return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def cross4(a,b,c):  # vector orthogonal to a,b,c in R^4
    M=[a,b,c]; out=[]
    for k in range(4):
        cols=[i for i in range(4) if i!=k]
        out.append((-1)**k*det3(*[[row[i] for i in cols] for row in M]))
    return tuple(out)
def norm(v):
    g=0
    from math import gcd
    for x in v: g=gcd(g,abs(x))
    v=tuple(x//g for x in v)
    return v if v>tuple(-x for x in v) else tuple(-x for x in v)
dot=lambda a,b: sum(x*y for x,y in zip(a,b))
normals=set()
for a,b,c in itertools.combinations(D4,3):
    n=cross4(a,b,c)
    if any(n): normals.add(norm(n))
cnt={n:sum(1 for r in D4 if dot(n,r)==0) for n in normals}
big=[n for n in normals if cnt[n]>=6]; print('hyperplanes',len(normals),'with >=6 roots',len(big),'max',max(cnt.values()))
D4n=set(norm(r) for r in D4)
sols=0
for five in itertools.combinations(big,5):
    ok=True; seen=set()
    for T in itertools.combinations(five,3):
        x=cross4(*T)       # intersection line of the three hyperplanes (normal-of-normals)
        if not any(x): ok=False; break
        x=norm(x)
        if x not in D4n or x in seen: ok=False; break
        seen.add(x)
    if ok: sols+=1
print('valid 5-configs',sols)
# pigeonhole lemma check: pairs of big hyperplanes and #roots in their intersection
from collections import Counter
print('pair intersections #roots:',Counter(sum(1 for r in D4 if dot(n,r)==0 and dot(m,r)==0) for n,m in itertools.combinations(big,2)))
