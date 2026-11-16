# CARRIER lib: E8 lines, labels (F2^9), frame (8 orthogonal lines), P112, directions.  Exact ints.
import itertools
roots=[]
for i,j in itertools.combinations(range(8),2):
    for si in (2,-2):
        for sj in (2,-2):
            v=[0]*8; v[i]=si; v[j]=sj; roots.append(tuple(v))
for signs in itertools.product((1,-1),repeat=8):
    if signs.count(-1)%2==0: roots.append(signs)
def canon(v):
    for x in v:
        if x: return v if x>0 else tuple(-y for y in v)
lines=sorted({canon(r) for r in roots}); n=len(lines)
ip=lambda a,b: sum(x*y for x,y in zip(a,b))//4
simple=[(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)]
from fractions import Fraction as Fr
def solve(Mcols,b):
    m=len(Mcols); A=[[Fr(Mcols[c][r]) for c in range(m)]+[Fr(b[r])] for r in range(8)]
    piv=[];row=0
    for c in range(m):
        p=next((r for r in range(row,8) if A[r][c]!=0),None)
        if p is None: continue
        A[row],A[p]=A[p],A[row]; inv=1/A[row][c]; A[row]=[x*inv for x in A[row]]
        for r in range(8):
            if r!=row and A[r][c]!=0:
                f=A[r][c]; A[r]=[x-f*y for x,y in zip(A[r],A[row])]
        piv.append(c); row+=1
    x=[Fr(0)]*m
    for r,c in enumerate(piv): x[c]=A[r][m]
    return x
lab=[]
for l in lines:
    x=solve(simple,l); assert all(v.denominator==1 for v in x)
    lab.append(1|sum((int(v)%2)<<(k+1) for k,v in enumerate(x)))
par=lambda x: bin(x).count('1')&1
def f2rank(vs):
    b=[]
    for x in vs:
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return len(b)
# frame: (e1+e2),(e1-e2),(e3+e4),(e3-e4),... doubled coords
frame=[]
for k in range(4):
    for s in (2,-2):
        v=[0]*8; v[2*k]=2; v[2*k+1]=s; frame.append(canon(tuple(v)))
fidx=[lines.index(f) for f in frame]
P=[i for i in range(n) if i not in fidx]   # P112
