"""Deterministically build FRAMES27.json: 27 mode-preserving frames attaining the
near-optimal depth-27 zero-fiber pattern (rank-3 stage maps onto E).

Usage: python3 build_frames.py OUT.json   (verify.py does not trust this derivation)
"""
import json, pathlib, random, sys
HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = HERE.parent / "precision-state-frontier" / "FIXTURE.json"
cols=json.loads(FIXTURE.read_text())['mode_columns']
rows=[tuple(cols[j][i] for j in range(8)) for i in range(112)]
rows=[tuple(cols[j][i] for j in range(8)) for i in range(112)]
EIDX=[0,1,2,4]; free=[i for i in range(112) if i not in EIDX]
# integer kernel basis of A (8 x 108) by unimodular column ops: A U = [H|0]
A=[[rows[i][k] for i in free] for k in range(8)]
n=len(free); U=[[int(i==j) for j in range(n)] for i in range(n)]  # U columns
def colop(c1,c2,f):  # col c1 -= f*col c2
    for r in A: r[c1]-=f*r[c2]
    for r in U: r[c1]-=f*r[c2]
def swap(c1,c2):
    for r in A: r[c1],r[c2]=r[c2],r[c1]
    for r in U: r[c1],r[c2]=r[c2],r[c1]
piv=0
for k in range(8):
    while True:
        nz=[c for c in range(piv,n) if A[k][c]!=0]
        if len(nz)<=1: break
        c0=min(nz,key=lambda c:abs(A[k][c]))
        for c in nz:
            if c!=c0: colop(c,c0,A[k][c]//A[k][c0])
    nz=[c for c in range(piv,n) if A[k][c]!=0]
    if nz: swap(piv,nz[0]); piv+=1
assert piv==8
kern=[[U[i][c] for i in range(n)] for c in range(8,n)]
for v in kern:
    for k in range(8): assert sum(rows[free[i]][k]*v[i] for i in range(n))==0
full=[]
for v in kern:
    w=[0]*112
    for i,x in zip(free,v): w[i]=x
    full.append(w)
kern=full
from fractions import Fraction
EIDX=[0,1,2,4]; T=27
wt=lambda u:bin(u).count('1')
par=lambda i,q: sum(rows[i][k] for k in range(8) if q>>k&1)&1
eta=lambda q: sum(par(EIDX[b],q)<<b for b in range(4))
C=[q for q in range(256) if all(par(i,q)==0 for i in range(112))]; assert len(C)==16
assert all(eta(c)==0 for c in C) and len({eta(q) for q in range(256)})==16
etaE={eta(q) for q in range(256) if wt(q)%2==0}; assert len(etaE)==8
# linear maps F2^4->F2^4 as list of 4 images of basis
def ap(L,x):
    y=0
    for b in range(4):
        if x>>b&1: y^=L[b]
    return y
rng=random.Random(20)
klines=(list(range(1,16))*2)[:T]
def rand_map(k):
    while True:
        L=[rng.choice(sorted(etaE)) for _ in range(4)]
        if {ap(L,x) for x in range(16)}==etaE and ap(L,k)==0: return L
while True:
    Ls=[rand_map(k) for k in klines[:-1]]
    last=[0]*4
    for L in Ls: last=[a^b for a,b in zip(last,L)]
    if {ap(last,x) for x in range(16)}==etaE and ap(last,klines[-1])==0: Ls.append(last); break
# psi_j : F2^4 -> R' in kernel-basis coordinates (100-bit ints); psi_1 = 0
NB=len(kern)
MS=5   # number of maps solved at the end
psi=[[0]*4]+[[rng.getrandbits(NB) for _ in range(4)] for _ in range(T-1-MS)]
Phi=[0]*4   # on basis x=1,2,4,8
for j in range(1,T-MS):
    for b in range(4): Phi[b]^=ap(psi[j],ap(Ls[j],1<<b))
solved=list(range(T-MS,T))
# unknown bits per coordinate: a_{i,t} (i in solved, t in 0..3); equation for basis x_b: sum_i sum_t a_{i,t} [ (l_i x_b)_t ] = target_b
nv=4*MS
eqs=[]
for b in range(4):
    row=0
    for ii,i in enumerate(solved):
        y=ap(Ls[i],1<<b)
        for t in range(4):
            if y>>t&1: row|=1<<(4*ii+t)
    eqs.append(row)
# gaussian elimination over F2 with RHS symbolic per coordinate: reduce eqs, track combination of b
red=[]; 
for b,r in enumerate(eqs):
    comb=1<<b
    for (pr,pc,pp) in red:
        if r>>pp&1: r^=pr; comb^=pc
    if r: red.append((r,comb,r.bit_length()-1))
    else: assert False,'dependent equations'
# back-substitute to reduced row echelon
for i in range(len(red)):
    r,c,p=red[i]
    for j in range(len(red)):
        if j!=i and red[j][0]>>p&1: red[j]=(red[j][0]^r,red[j][1]^c,red[j][2])
pivots={p for _,_,p in red}; freev=[v for v in range(nv) if v not in pivots]
out=[[0]*4 for _ in solved]
for c in range(NB):
    tgt=[Phi[b]>>c&1 for b in range(4)]
    a=0
    for v in freev:
        if rng.getrandbits(1): a|=1<<v
    for r,cb,p in red:
        rhs=0
        for b in range(4):
            if cb>>b&1: rhs^=tgt[b]
        val=rhs^(bin(r&a&~(1<<p)).count('1')&1)
        if val: a|=1<<p
    for ii in range(MS):
        for t in range(4):
            if a>>(4*ii+t)&1: out[ii][t]|=1<<c
psi+=out
assert len(psi)==T
# integer frames: V_j column t = sum of kernel vectors selected by psi_j[t]
V=[]
for j in range(T):
    Vj=[]
    for t in range(4):
        v=[0]*112
        for b in range(NB):
            if psi[j][t]>>b&1: v=[x+y for x,y in zip(v,kern[b])]
        Vj.append(v)
    V.append(Vj)
sparse=[[{str(i):x for i,x in enumerate(v) if x} for v in Vj] for Vj in V]
json.dump({'seed':20,'kernel_lines':klines,'stage_maps_eta':Ls,'V_columns_sparse':sparse},open(sys.argv[1],'w'),indent=0,sort_keys=True)
open(sys.argv[1],'a').write('\n')
print('built; nonzero V entries',sum(1 for Vj in V for v in Vj for x in v if x))
