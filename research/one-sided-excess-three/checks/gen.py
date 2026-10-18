# Regenerates data.txt (labels, frame labels, 112 line coordinates, direction list |Off|<=77) and gens.txt (orbit generators).
# Independent data generation (own coordinates, own labels, own direction list, own group/orbits).
# Coordinates doubled (integers). E8 = D8 ∪ D8+(1/2)^8, roots norm 2 -> doubled norm 8.
import itertools, numpy as np, sys, random
from fractions import Fraction
OUT=''   # write into the current directory
LIM=int(sys.argv[1]) if len(sys.argv)>1 else 77
DATA='data.txt' if LIM==77 else 'data%d.txt'%LIM
roots=[]
for i,j in itertools.combinations(range(8),2):
    for si in (2,-2):
        for sj in (2,-2):
            v=[0]*8; v[i]=si; v[j]=sj; roots.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: roots.append(tuple(s))
assert len(roots)==240
def dot(a,b): return sum(x*y for x,y in zip(a,b))//4   # true inner product (doubled coords)
lines=sorted({max(r,tuple(-x for x in r)) for r in roots}); assert len(lines)==120
frame=[]
for k in range(4):
    a=[0]*8; a[2*k]=2; a[2*k+1]=2; frame.append(tuple(a))
    b=[0]*8; b[2*k]=2; b[2*k+1]=-2; frame.append(tuple(b))
frame=[max(f,tuple(-x for x in f)) for f in frame]
for f,g in itertools.combinations(frame,2): assert dot(f,g)==0
P=[l for l in lines if l not in frame]; assert len(P)==112
# labels: coordinates of r in a Z-basis of E8, mod 2; basis = simple roots (Bourbaki, doubled)
simple=[(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)]
M=np.array(simple,dtype=float).T
assert abs(abs(np.linalg.det(np.array([[dot(a,b) for b in simple] for a in simple],dtype=float)))-1)<1e-9
def lab(r):
    n=np.linalg.solve(M,np.array(r,dtype=float)); ni=np.rint(n).astype(int); assert np.allclose(n,ni)
    x=1
    for k in range(8): x|=(int(ni[k])&1)<<(k+1)
    return x
LAB=[lab(r) for r in P]; assert len(set(LAB))==112
ZL=[lab(f) for f in frame]
# F2 rank of all labels =9
def f2rank(vs):
    bs=[]
    for x in vs:
        for b in bs: x=min(x,x^b)
        if x: bs.append(x)
    return len(bs)
assert f2rank(LAB)==9
# directions: E8 vectors of norm <= 8 (doubled norm <=32), primitive up to sign
vecs=set()
rng2=range(-6,7,2); rng1=range(-5,6,2)
for v in itertools.product(rng2,repeat=8):
    if 0<sum(x*x for x in v)<=32 and (sum(v)//2)%2==0: vecs.add(v)
for v in itertools.product(rng1,repeat=8):
    if sum(x*x for x in v)<=32 and ((sum(v)//2)%2==0): vecs.add(v)
# D8 membership: integer coords (v/2) with even sum -> doubled coords even, sum(v)/2 even. half: v odd, sum(v/2) even.
def prim(v):
    from math import gcd
    g=0
    for x in v: g=gcd(g,abs(x))
    v=tuple(x//g for x in v)
    return max(v,tuple(-x for x in v))
dirs={}
for v in vecs:
    p=prim(v); dirs.setdefault(p,v)
def off(h): return [t for t,r in enumerate(P) if sum(a*b for a,b in zip(r,h))!=0]
fin=[]
from collections import Counter
C=Counter()
for p,v in dirs.items():
    o=off(p)
    if len(o)<=LIM:
        nE8=sum(1 for l in lines if sum(a*b for a,b in zip(l,p))==0)
        C[(sum(x*x for x in v)//4,nE8,len(o))]+=1; fin.append((p,o))
print('finite directions |Off|<=77 by (norm,E8 lines perp,|Off|):',sorted(C.items()))
# pencils: A2 planes span(a,b), a.b=-1 ; generic Off = lines not perp to both
pen={}
for a,b in itertools.combinations(lines,2):
    if abs(dot(a,b))==1:
        perp=frozenset(t for t,r in enumerate(P) if dot(r,a)==0 and dot(r,b)==0)
        key=frozenset(l for l in lines if dot(l,a)==0 and dot(l,b)==0)
        pen.setdefault(key,(a,b,perp))
pens=[]
CP=Counter()
for key,(a,b,perp) in pen.items():
    o=[t for t in range(112) if t not in perp]
    CP[(len(key),len(o))]+=1
    if len(o)<=LIM: pens.append((a,b,o))
print('A2 planes (E8 lines perp, generic |Off|):',sorted(CP.items()))
with open(OUT+DATA,'w') as f:
    f.write(' '.join(map(str,LAB))+'\n')
    f.write(' '.join(map(str,ZL))+'\n')
    for r in P: f.write(' '.join(map(str,r))+'\n')
    f.write('%d\n'%(len(fin)+len(pens)))
    for p,o in fin: f.write('1 '+' '.join(map(str,p))+' : '+' '.join(map(str,o))+'\n')
    for a,b,o in pens: f.write('2 '+' '.join(map(str,a))+' '+' '.join(map(str,b))+' : '+' '.join(map(str,o))+'\n')
print('wrote',len(fin),'finite',len(pens),'pencils')
# group: sign flips (reflections in frame roots) and coordinate-permutations of frame preserving supports
def refl(f):
    return lambda r: tuple(x - (2*sum(a*b for a,b in zip(r,f))//sum(y*y for y in f))*y for x,y in zip(r,f))
idx={r:t for t,r in enumerate(P)}
def lineperm(g):
    out=[]
    for r in P:
        s=g(r); s=max(s,tuple(-x for x in s)); out.append(idx[s])
    return out
gens=[lineperm(refl(f)) for f in frame]
# permutation part: c-coordinates c_j = r.f_j ; map c -> c∘pi^{-1}; r = sum c_j f_j /2
Fm=np.array(frame,dtype=float)
def cvec(r): return [dot(r,f) for f in frame]
supps={frozenset(j for j,c in enumerate(cvec(r)) if c) for r in P}
assert len(supps)==14 and all(len(s)==4 for s in supps)
auts=[pi for pi in itertools.permutations(range(8)) if all(frozenset(pi[j] for j in s) in supps for s in supps)]
print('Aut(Hamming) order',len(auts))
random.seed(1)
def mk(pi):
    def g(r):
        c=cvec(r); c2=[0]*8
        for j in range(8): c2[pi[j]]=c[j]
        v=sum(c2[j]*Fm[j] for j in range(8))/2
        vi=tuple(int(round(x)) for x in v); return vi
    return g
for _ in range(4): gens.append(lineperm(mk(random.choice(auts))))
# check group size generated on lines
import collections
def gsize(gens,limit=10**6):
    I=tuple(range(112)); seen={I}; st=[I]
    while st:
        x=st.pop()
        for g in gens:
            y=tuple(g[i] for i in x)
            if y not in seen:
                seen.add(y); st.append(y)
                if len(seen)>limit: return -1
    return len(seen)
print('group order on lines',gsize(gens))
# label linearity of each generator: map must be induced by a linear map of F2^9
for g in gens:
    # solve linear map from a basis of labels
    bs=[];imgs=[]
    for t in range(112):
        x=LAB[t]; y=LAB[g[t]]; xx=x; yy=y
        for b,ib in zip(bs,imgs):
            if (xx^b)<xx: xx^=b; yy^=ib
        if xx: bs.append(xx); imgs.append(yy)
        else: assert yy==0, 'nonlinear'
with open(OUT+'gens.txt','w') as f:
    for g in gens: f.write(' '.join(map(str,g))+'\n')
print('gens ok, linear on labels')
