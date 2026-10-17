# SIX independent re-implementation of Lemma S66(+t). Different coordinates (frame c-coordinates), different labels
# (Gram mod 2 against a random unimodular root basis), directions from sums of orthogonal roots (checked against the
# E8 theta series 240/2160/6720), subspaces by RREF enumeration, own orbit code, numpy-vectorised over V2.
import itertools, numpy as np, random, sys
from fractions import Fraction
mode=int(sys.argv[1]); CH=int(sys.argv[2]) if len(sys.argv)>2 else 0; NCH=int(sys.argv[3]) if len(sys.argv)>3 else 1   # 0: |Off|<=76, X = Λ(V1)∪Λ(V2);  1: |Off|<=77, plus one free line per h
# Hamming [8,4,4] supports
G=[0b11110000,0b11001100,0b10101010,0b11111111]
code=set()
for m in range(16):
    x=0
    for i in range(4):
        if m>>i&1: x^=G[i]
    code.add(x)
supp4=[c for c in code if bin(c).count('1')==4]; assert len(supp4)==14
# roots in c-coords (c_j = <r,f_j>): frame roots 2e_j, others ±1 on a weight-4 support; <r,s> = c.c'/2
R=[]
for j in range(8):
    v=[0]*8; v[j]=2; R.append(tuple(v)); R.append(tuple(-x for x in v))
for s in supp4:
    pos=[j for j in range(8) if s>>j&1]
    for sg in itertools.product((1,-1),repeat=4):
        v=[0]*8
        for p,g in zip(pos,sg): v[p]=g
        R.append(tuple(v))
assert len(R)==240
ip=lambda a,b: Fraction(sum(x*y for x,y in zip(a,b)),2)
for r in R: assert ip(r,r)==2
assert all(ip(a,b).denominator==1 for a in R[:40] for b in R)
canon=lambda v: max(tuple(v),tuple(-x for x in v))
P=sorted({canon(r) for r in R if sum(1 for x in r if x)==4}); assert len(P)==112
# labels: (1, <r,b_k> mod 2) for a unimodular basis b of E8 made of roots
random.seed(7)
while True:
    B=random.sample(R,8)
    Gm=np.array([[float(ip(a,b)) for b in B] for a in B])
    if abs(abs(np.linalg.det(Gm))-1)<1e-6: break
LAB=[1|sum(((int(ip(r,b))&1)<<(k+1)) for k,b in enumerate(B)) for r in P]
assert len(set(LAB))==112
# directions: primitive vectors h (in c-coords, up to scale) from sums of pairwise orthogonal roots (1,2,3 roots)
def prim(v):
    from math import gcd
    g=0
    for x in v: g=gcd(g,abs(int(x)))
    return canon([int(x)//g for x in v])
vecs={1:set(),2:set(),3:set()}
Rl=R
for a in Rl: vecs[1].add(a)
for a,b in itertools.combinations(Rl,2):
    if ip(a,b)==0: vecs[2].add(tuple(x+y for x,y in zip(a,b)))
orth={a:[b for b in Rl if ip(a,b)==0] for a in Rl}
for a in Rl:
    for b in orth[a]:
        for c in orth[a]:
            if ip(b,c)==0 and b<c: vecs[3].add(tuple(x+y+z for x,y,z in zip(a,b,c)))
n4={v for v in vecs[2] if ip(v,v)==4}; n6={v for v in vecs[3] if ip(v,v)==6}
print('norm2',len(vecs[1]),'norm4',len(n4),'norm6',len(n6),'(theta: 240 2160 6720)')
assert len(vecs[1])==240 and len(n4)==2160 and len(n6)==6720
dirs={}
for v in list(vecs[1])+list(n4)+list(n6): dirs.setdefault(prim(v),v)
def offmask(h):
    m=0
    for t,r in enumerate(P):
        if sum(x*y for x,y in zip(r,h))!=0: m|=1<<t
    return m
D=[]
lim=76  # mode 1 also uses the 1200-list: E6+A1 (|Off|=77, cap 32) cannot qualify since |X ∪ t| <= 41 < 45
for h in dirs:
    m=offmask(h)
    if bin(m).count('1')<=lim: D.append((h,m))
print('directions with |Off|<=%d:'%lim,len(D))
# A2 pencils: generic Off = lines not perp to both roots of an A2
pmin=min(bin(sum(1<<t for t,r in enumerate(P) if not (sum(x*y for x,y in zip(r,a))==0 and sum(x*y for x,y in zip(r,b))==0))).count('1')
         for a in Rl[:60] for b in Rl if ip(a,b)==-1)
print('min generic |Off| over A2 pencils (sample of a):',pmin)
def split(m): return (m & ((1<<64)-1), m>>64)
# parity table
par=np.array([[bin(w&l).count('1')&1 for l in LAB] for w in range(512)],dtype=bool)
def lines_of_dual(ws):
    ok=np.ones(112,dtype=bool)
    for w in ws: ok&=~par[w]
    m=0
    for t in np.nonzero(ok)[0]: m|=1<<int(t)
    return m
# 7-flats: dual 2-dim; caps
seen=set(); F7=[]
for w1 in range(1,512):
    for w2 in range(w1+1,512):
        if (w1^w2)<w2: continue
        F7.append(lines_of_dual([w1,w2]))
print('7-flats',len(F7))
F7a=np.array([split(m) for m in F7],dtype=np.uint64)
def pcarr(a): return np.bitwise_count(a[:,0]).astype(np.int32)+np.bitwise_count(a[:,1]).astype(np.int32)
Dm=np.array([split(m) for h,m in D],dtype=np.uint64)
cap=[int(pcarr(F7a & Dm[i]).max()) for i in range(len(D))]
print('caps',sorted(set(cap)))
# all 6-dim subspaces: duals = 3-dim subspaces in RREF (pivots p1<p2<p3, entries at non-pivot columns right of pivot... use RREF over bit positions)
masks=set()
cnt=0
for piv in itertools.combinations(range(9),3):
    # row i has leading 1 at piv[i] (highest bit convention: bits > piv[i] zero), zero at other pivots, free at non-pivot bits < piv[i]
    free=[[b for b in range(piv[i]) if b not in piv] for i in range(3)]
    for bits in itertools.product(*[range(1<<len(f)) for f in free]):
        ws=[]
        for i in range(3):
            w=1<<piv[i]
            for k,b in enumerate(free[i]):
                if bits[i]>>k&1: w|=1<<b
            ws.append(w)
        cnt+=1
        m=lines_of_dual(ws)
        if m: masks.add(m)
print('3-dim duals',cnt,'(expect 788035); distinct nonempty line sets',len(masks))
masks=sorted(masks); idx={m:i for i,m in enumerate(masks)}
# group: sign flips and Hamming permutations, acting on c-coords
auts=[pi for pi in itertools.permutations(range(8)) if all(sum(1<<pi[j] for j in range(8) if s>>j&1) in code for s in supp4)]
pidx={r:t for t,r in enumerate(P)}
def act(fn): return [pidx[canon(fn(r))] for r in P]
gens=[act(lambda r,j=j: tuple(-x if k==j else x for k,x in enumerate(r))) for j in range(8)]
random.seed(3)
for _ in range(3):
    pi=random.choice(auts)
    gens.append(act(lambda r,pi=pi: tuple(r[pi.index(k)] for k in range(8))))
# byte tables for fast mask mapping
def table(g):
    T=[]
    for byte in range(14):
        row=[]
        for v in range(256):
            o=0
            for b in range(8):
                if v>>b&1 and byte*8+b<112: o|=1<<g[byte*8+b]
            row.append(o)
        T.append(row)
    return T
TB=[table(g) for g in gens]
def mp(m,T):
    o=0; k=0
    while m:
        o|=T[k][m&255]; m>>=8; k+=1
    return o
parent=list(range(len(masks)))
def fd(x):
    while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
    return x
for i,m in enumerate(masks):
    for T in TB:
        j=idx[mp(m,T)]; a,b=fd(i),fd(j)
        if a!=b: parent[a]=b
reps=[i for i in range(len(masks)) if fd(i)==i]
print('orbits',len(reps))
X2=np.array([split(m) for m in masks],dtype=np.uint64)
def f2rank(m):
    bs=[]
    t=0
    while m:
        if m&1:
            x=LAB[t]
            for b in bs: x=min(x,x^b)
            if x: bs.append(x)
        m>>=1; t+=1
    return len(bs)
def ok_h(m):
    if mode==0: return f2rank(m)<=7
    # rank(R minus one line) <= 7  <=>  rank(R) <= 7, or rank(R) = 8 and some hyperplane of span(R) misses at most one line of R
    labs=[LAB[t] for t in range(112) if m>>t&1]
    bs=[]; 
    for x in labs:
        for b in bs: x=min(x,x^b)
        if x: bs.append(x)
    r=len(bs)
    if r<=7: return True
    if r>8: return False
    # coordinates w.r.t. a basis chosen among the labels: Gaussian elimination tracking combinations
    piv=[]  # (pivot vector reduced, coord bitmask)
    for x in labs:
        c=0; y=x
        for (pv,pc) in piv:
            if (y^pv)<y: y^=pv; c^=pc
        if y: piv.append((y,c|(1<<len(piv))))
    co=[]
    for x in labs:
        c=0; y=x
        for (pv,pc) in piv:
            if (y^pv)<y: y^=pv; c^=pc
        assert y==0; co.append(c)
    cnt=PAR8[np.array(co)].sum(axis=0)
    return bool((cnt[1:]<=1).any())
def qrank(vs):
    rows=[[Fraction(x) for x in v] for v in vs]; r=0
    for c in range(8):
        p=next((i for i in range(r,len(rows)) if rows[i][c]!=0),None)
        if p is None: continue
        rows[r],rows[p]=rows[p],rows[r]
        for i in range(len(rows)):
            if i!=r and rows[i][c]!=0:
                f=rows[i][c]/rows[r][c]; rows[i]=[a-f*b for a,b in zip(rows[i],rows[r])]
        r+=1
    return r
slack=1 if mode==1 else 0
PAR8=np.array([[bin(a&b).count('1')&1 for b in range(256)] for a in range(256)],dtype=np.int32)
best=0; bestn=0
done=[]
for ri,i in enumerate(reps):
    if ri%NCH!=CH: continue
    done.append(ri)
    X1=masks[i]; hits={}
    for hi,(h,m) in enumerate(D):
        r1=m & ~X1
        if bin(r1).count('1')>cap[hi]+20+slack: continue
        a=np.array(split(r1),dtype=np.uint64)
        rr=np.empty_like(X2); rr[:,0]=a[0]&~X2[:,0]; rr[:,1]=a[1]&~X2[:,1]
        cand=np.nonzero(pcarr(rr)<=cap[hi]+slack)[0]
        for j in cand:
            rm=int(rr[j,0])|(int(rr[j,1])<<64)
            if ok_h(rm): hits.setdefault(int(j),[]).append(h)
    for j,hs in hits.items():
        bestn=max(bestn,len(hs))
        best=max(best,qrank(hs))
    if ri%20==0: print('rep',ri,'running max rank',best,'max #h',bestn,flush=True)
print('DONE REPS',done)
print('INDEP OVERALL mode',mode,'chunk',CH,NCH,': max real rank',best,'max #directions',bestn)
