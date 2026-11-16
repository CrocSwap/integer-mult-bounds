# AUDIT-IMP independent rebuild (no repo data files): E8, frame, P112, labels, directions, catalogue, L3.1, g-table.
# Writes dirs.txt (for pc2.c) and prints checks. Run: W/venv/bin/python ind_e8.py
import itertools, numpy as np
from fractions import Fraction as Fr
from collections import Counter
R=[]
for i,j in itertools.combinations(range(8),2):
    for a in (1,-1):
        for b in (1,-1):
            v=[0]*8; v[i]=2*a; v[j]=2*b; R.append(tuple(v))          # doubled coords
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(tuple(s))
assert len(R)==240
ip=lambda a,b: sum(x*y for x,y in zip(a,b))//4                      # true inner product
lines=[]; seen=set()
for r in R:
    if tuple(-x for x in r) in seen: continue
    seen.add(r); lines.append(r)
assert len(lines)==120
F0=[]
for k in range(4):
    for sg in (1,-1):
        v=[0]*8; v[2*k]=2; v[2*k+1]=2*sg; F0.append(tuple(v))
assert all(ip(a,b)==(2 if a==b else 0) for a in F0 for b in F0)
Fs=set(F0)|{tuple(-x for x in f) for f in F0}
L=[r for r in lines if r not in Fs]; v=len(L); assert v==112
# Z-basis of E8 (doubled coords), coordinates by exact solve
B=[[4,0,0,0,0,0,0,0]]+[[0]*i+[-2,2]+[0]*(6-i) for i in range(6)]+[[1]*8]
Bm=np.array(B,dtype=float); assert abs(abs(np.linalg.det(Bm/2))-1)<1e-9
Binv=np.linalg.inv(Bm.T)
def coords(x):
    c=Binv@np.array(x,dtype=float); ci=np.rint(c).astype(int); assert np.allclose(c,ci); return ci
G=np.array([[ip(a,b) for b in B] for a in B])%2
def lab(x):  # (1, x mod 2E8) as 9-bit int; bit0 = the F2 coordinate
    c=coords(x)%2; return 1|sum(int(c[i])<<(i+1) for i in range(8))
def beta(u,w):
    a=u&1; b=w&1; x=np.array([(u>>(i+1))&1 for i in range(8)]); y=np.array([(w>>(i+1))&1 for i in range(8)])
    return (a*b+int(x@G@y))%2
LAB=[lab(r) for r in L]; assert len(set(LAB))==112
for t in range(v):
    for s in range(v):
        bd=1 if (t==s or ip(L[t],L[s])==0) else 0
        assert beta(LAB[t],LAB[s])==bd
Zf=[lab(f) for f in F0]
# rank over F2 of a list of 9-bit ints
def rk(xs):
    basis=[]
    for x in xs:
        for b in basis: x=min(x,x^b)
        if x: basis.append(x)
    return len(basis)
assert rk(LAB)==9
BT=[[beta(1<<i,1<<j) for j in range(9)] for i in range(9)]
def bz(u,z): return beta(u,z)
O={z: frozenset(s for s in range(v) if bz(LAB[s],z)) for z in range(1,512)}
pk=lambda S: sum(1<<i for i in S)
# g-table via annihilators: lines with labels in a codim-c subspace
g8=max(v-len(O[z]) for z in O); print('g(8)=',g8, ' min|O_z|=',min(len(x) for x in O.values()))
g7=0
for z1 in range(1,512):
    for z2 in range(z1+1,512):
        n=v-len(O[z1]|O[z2]|O[z1^z2]); g7=max(g7,n)
print('g(7)=',g7)
# directions: E8 vectors of norm 2,4,6 (doubled coords: norm*4), up to sign
def vecs(norm):
    out=set()
    rng=range(-6,7)
    # even-coordinate type (all doubled coords even) and odd type
    for par in (0,1):
        cand=[x for x in rng if x%2==par]
        def rec(pre,rem):
            if len(pre)==8:
                if rem==0: yield tuple(pre)
                return
            for x in cand:
                if x*x<=rem: yield from rec(pre+[x],rem-x*x)
        for x in rec([],4*norm):
            if par==0 and (sum(x)//2)%2: continue        # D8: sum of true coords even
            if par==1 and (sum(x)//1)%4: continue          # D8+1/2: sum of true coords even
            nx=tuple(-y for y in x)
            if nx not in out: out.add(x)
    return out
allv={n:vecs(n) for n in (2,4,6,8)}
print('vector counts (up to sign)',{n:len(allv[n]) for n in allv})
assert len(allv[2])==120 and len(allv[4])==1080
off=lambda h: frozenset(t for t in range(v) if ip(L[t],h)!=0)
dirs=[]
for n in (2,4,6,8):  # norm 8 printed only (|Off|<=76 there = 2*roots, non-primitive)
    c=Counter()
    for h in allv[n]:
        o=off(h); c[len(o)]+=1
        if len(o)<=76 and n<8: dirs.append((n,h,o))
    print('norm',n,'|Off|<=80 dist',sorted((k,c[k]) for k in c if k<=80), 'min',min(c))
print('directions with |Off|<=76:',len(dirs),Counter((n,len(o)) for n,h,o in dirs))
# E6 subsystems (centralisers of A2): frame lines inside, P112 lines inside
mn=99; mx=0; nA2=0
for a,b in itertools.combinations(R,2):
    if ip(a,b)==-1:
        perp=[r for r in lines if ip(r,a)==0 and ip(r,b)==0]
        nf=sum(1 for r in perp if r in Fs); mn=min(mn,nf); mx=max(mx,len(perp)-nf); nA2+=1
print('A2 pairs',nA2,'min frame lines in E6',mn,'max P112 lines in E6',mx)
# L3.1: label hyperplanes (z) whose complement O_z has real rank <=7
def realrank(S): return np.linalg.matrix_rank(np.array([L[s] for s in S],dtype=float)) if S else 0
bad=[z for z in O if realrank(O[z])<=7]
print('L3.1: hyperplanes with complement rank<=7:',len(bad),'= frame classes:',sorted(bad)==sorted(Zf))
# catalogue: min_z |O_z ∩ Off(h)| over all 511 z
cat=Counter(); viol=[]
fidx={f:i for i,f in enumerate(F0)}
for n,h,o in dirs:
    vals=sorted((len(O[z]&o),z) for z in O)
    m0=vals[0][0]
    kind='frame' if (n==2 and (h in Fs or tuple(-x for x in h) in Fs)) else ('root' if n==2 else 'n%d'%n)
    cat[(kind,len(o),m0,vals[1][0])]+=1
    for val,z in vals:
        if val>11: break
        if val==0:
            ok = kind=='frame' and z==lab(h)
        elif val==1:
            w=next(iter(O[z]&o)); ok = kind=='root' and z==LAB[w] and lab(h)==LAB[w]
        else: ok=False
        if not ok: viol.append((kind,len(o),val))
print('catalogue (kind,|Off|,min,next):',dict(cat)); print('catalogue violations (<=11 not of type 0-frame/1-rootswap):',viol)
with open('dirs.txt','w') as fh:
    fh.write(' '.join(map(str,LAB))+'\n')
    for n,h,o in dirs:
        if len(o)<=72: fh.write('%s %d %s\n'%('F' if h in Fs or tuple(-x for x in h) in Fs else ('R' if n==2 else 'N'),len(o),' '.join(map(str,sorted(o)))))
print('wrote dirs.txt')
