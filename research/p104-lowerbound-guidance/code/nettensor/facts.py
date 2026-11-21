# NETTENSOR facts.py (own code): exact P104 facts used in NT.md.
import re, numpy as np, itertools
B='<research-tree>/'
G=np.load(B+'cards/WILD/REBASET1/G104.npy').astype(int)
s=open(B+'lean/decoder-duality/Nov15/DecoderWall4Data.lean').read(); i=s.index('def labs')
q=[int(x) for x in re.findall(r'\d+', s[i:s.index(']',i)])]
n=104; FR=[0,6,16,22,29,36,45,95]; Ah=G[:,FR]
dot=lambda a,b: bin(a&b).count('1')&1
assert (Ah@Ah.T==2*G).all()
IP=(Ah@Ah.T)//2  # root inner products (Ah = scaled roots, norm 2 after /2)
# (a) label form vs root form mod 2
bad=sum(1 for s_ in range(n) for p in range(n) if dot(q[s_],q[p]) != (1+IP[s_,p])%2)
print('(a) q.q\' == 1+<r,r\'> mod 2 violations:',bad, ' distinct labels:',len(set(q)), 'IP values',sorted(set(IP.flatten())))
# (b) N(f): max labels in f-dim subspace; and codim-2 root rank fact
def span(vs):
    S={0}
    for v in vs:
        if v not in S: S=S|{x^v for x in S}
    return S
# linear map L: F2^9 -> F2^8 with L(q_s) = r_s mod 2 ?
R2=[int(''.join(str(int(x)%2) for x in Ah[t]//1),2) for t in range(n)]  # placeholder (Ah scaled) -> recompute below
# roots r = Ah/sqrt2 not integral; use lattice coords: E8 form mod 2 is IP mod 2; test linearity via IP only:
# q.q' + 1 + IP mod 2 == 0 already; test whether the map q -> (IP[s,:] mod 2) is affine-linear on labels
import functools
M2=(IP%2).astype(int)
def f2solve_lin(rows_in, rows_out):
    # check: exists linear L with L(q_s)=out_s  <=> every F2 relation among q_s holds among out_s
    basis={}  # pivot -> (vec, combo of outs)
    for v,o in zip(rows_in,rows_out):
        while v:
            p=v.bit_length()-1
            if p in basis: bv,bo=basis[p]; v^=bv; o^=bo
            else: basis[p]=(v,o); break
        else:
            if o: return False
    return True
outs=[int(''.join(str(x) for x in M2[t]),2) for t in range(n)]
print('(a2) t -> row of <r_t,.> mod 2 is LINEAR in q_t:',f2solve_lin(q,outs))
# odd cliques: maximal pairwise-odd sets of size 8
ODD=[[dot(q[a],q[b]) for b in range(n)] for a in range(n)]
cl=[]
def ext(c,cand):
    if len(c)==8: cl.append(tuple(c)); return
    for i,v in enumerate(cand):
        ext(c+[v],[w for w in cand[i+1:] if ODD[v][w]])
ext([],list(range(n)))
print('(c) odd 8-cliques:',len(cl))
# 13-partition by exact cover search
import sys; sys.setrecursionlimit(10000)
byv={v:[c for c in cl if v in c] for v in range(n)}
def cover(used,chosen):
    if len(used)==n: return chosen
    v=min(set(range(n))-used, key=lambda v: sum(1 for c in byv[v] if not used&set(c)))
    for c in byv[v]:
        if not used&set(c):
            r=cover(used|set(c),chosen+[c])
            if r: return r
    return None
part=cover(set(),[])
print('(c) partition found:',len(part))
from fractions import Fraction
import sympy
AhM=sympy.Matrix(Ah.tolist())
P_=1000003
def rkp(rows):
    A=[[int(x)%P_ for x in Ah[t]] for t in rows]; r=0
    for c in range(8):
        piv=next((i for i in range(r,len(A)) if A[i][c]),None)
        if piv is None: continue
        A[r],A[piv]=A[piv],A[r]; inv=pow(A[r][c],P_-2,P_)
        for i in range(len(A)):
            if i!=r and A[i][c]:
                f=A[i][c]*inv%P_; A[i]=[(x-f*y)%P_ for x,y in zip(A[i],A[r])]
        r+=1
    return r
def qrank(rows):
    if not rows: return 0
    r=rkp(rows)
    return r if r==8 else sympy.Matrix([Ah[t].tolist() for t in rows]).rank()  # exact when <8
# kernel lines: hyperplanes v^perp with roots outside (q.v=1) of rank<=7
kern=[]; 
for v in range(1,512):
    out=[t for t in range(n) if dot(q[t],v)]
    if qrank(out)<=7: kern.append(v)
print('(d) hyperplanes with outside-root rank<=7:',len(kern),' normals that are labels:',sum(1 for v in kern if v in q))
# codim-2 fact: every 7-dim Y: roots outside Y rank 8 <=> no pair (v,w) with outside(v)u... Y=<v,w>^perp; outside = q.v=1 or q.w=1
bad2=0
for v in range(1,512):
    for w in range(v+1,512):
        out=[t for t in range(n) if dot(q[t],v) or dot(q[t],w)]
        if len(out)<8 or qrank(out)<8: bad2+=1
print('(b) codim-2 flats with outside root rank<8:',bad2)
