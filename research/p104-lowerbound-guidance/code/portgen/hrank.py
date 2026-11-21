# label rank h = rank_F2(J + G mod 2) for root-line port sets (BOARD R-14 rule). Own code.
import itertools
from fractions import Fraction as F
R=[]
for i,j in itertools.combinations(range(8),2):
    for a in (1,-1):
        for b in (1,-1):
            v=[0]*8; v[i]=a; v[j]=b; R.append(tuple(F(x) for x in v))
for signs in itertools.product((1,-1),repeat=8):
    if signs.count(-1)%2==0: R.append(tuple(F(s,2) for s in signs))
assert len(R)==240
def dot(x,y): return sum(a*b for a,b in zip(x,y))
lines=[]; seen=set()
for r in R:
    k=tuple(-x for x in r)
    if k in seen: continue
    seen.add(r); lines.append(r)
def rank2(rows):
    rows=[int(''.join(map(str,r)),2) for r in rows]; rk=0
    piv=[]
    for x in rows:
        for p in piv: x=min(x,x^p)
        if x: piv.append(x); rk+=1
    return rk
def h_of(L):
    n=len(L); M=[[ (1+int(dot(L[a],L[b])))%2 if a!=b else (1+int(dot(L[a],L[a])))%2 for b in range(n)] for a in range(n)]
    G=[[int(dot(L[a],L[b]))%2 for b in range(n)] for a in range(n)]
    return rank2(M), rank2(G)
a0=lines[0]
E7=[l for l in lines if dot(l,a0)==0]
b0=[l for l in E7][0]
E6=[l for l in E7 if dot(l,b0)==0 and any(dot(l,c)!=0 for c in [a0]) is False]
# E6 = lines orthogonal to an A2: pick a root c with dot(c,a0)=-1 (A2 = <a0,c>)
c=[r for r in R if dot(r,a0)==-1][0]
E6=[l for l in lines if dot(l,a0)==0 and dot(l,c)==0]
D8=[l for l in lines if all(x.denominator==1 for x in l)]
half=[l for l in lines if any(x.denominator==2 for x in l)]
D4=[l for l in lines if all(x.denominator==1 for x in l) and all(l[i]==0 for i in range(4,8))]
for name,L in (('P120',lines),('E7',E7),('E6',E6),('D8',D8),('halfspin64',half),('D4',D4)):
    print(name,len(L),'h=rank(J+G), rank G:',h_of(L))
