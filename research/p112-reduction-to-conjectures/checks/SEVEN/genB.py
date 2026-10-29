# impl B data: own E8 (even coordinate system, doubled), own simple roots, labels (1, coords mod 2), types via fundamental coweights
import itertools
from fractions import Fraction as Fr
R=[]
for i,j in itertools.combinations(range(8),2):
    for s in (2,-2):
        for u in (2,-2):
            v=[0]*8; v[i]=s; v[j]=u; R.append(tuple(v))
for m in range(256):
    v=tuple(1 if m>>k&1 else -1 for k in range(8))
    if sum(1 for x in v if x<0)%2==0: R.append(v)
L=sorted({max(r,tuple(-x for x in r)) for r in R})
# simple roots (Bourbaki-like, doubled): a1=(1,-1,-1,-1,-1,-1,-1,1)/2 ... use a different but valid basis
S=[(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)]
S=S[::-1]   # reversed order: independent indexing from lib
def solve(B,v):
    n=len(B); M=[[Fr(B[j][i]) for j in range(n)]+[Fr(v[i])] for i in range(8)]
    r=0; piv=[]
    for c in range(n):
        p=next((i for i in range(r,8) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]; M[r]=[x/M[r][c] for x in M[r]]
        for i in range(8):
            if i!=r and M[i][c]!=0: M[i]=[a-M[i][c]*b for a,b in zip(M[i],M[r])]
        piv.append(c); r+=1
    x=[Fr(0)]*n
    for i,c in enumerate(piv): x[c]=M[i][n]
    assert all(sum(x[j]*B[j][i] for j in range(n))==v[i] for i in range(8))
    return x
lab=[]
for l in L:
    x=solve(S,l); assert all(t.denominator==1 for t in x)
    lab.append(sum((int(t)%2)<<k for k,t in enumerate(x))<<1|1)
assert len(set(lab))==120
# coweights: w_k with <w_k,S_j>=delta (Gram inverse); Off(w_k)= lines with <w_k,l>!=0
G=[[sum(a*b for a,b in zip(S[i],S[j])) for j in range(8)] for i in range(8)]
dot=lambda a,b: sum(x*y for x,y in zip(a,b))
out=open('triB.in','w'); out.write(' '.join(map(str,lab))+'\n')
for k in range(8):
    # w_k ⊥ S_j (j!=k): solve linear system in R^8 via nullspace of the 7 simple roots
    rows=[S[j] for j in range(8) if j!=k]
    # find w with rows.w=0 : use cofactor via solving with an extra unit equation
    import random
    for trial in range(50):
        e=[random.randint(-3,3) for _ in range(8)]
        A=rows+[tuple(e)]
        try: w=solve(list(zip(*A)),[0]*7+[1]) if False else None
        except AssertionError: w=None
        break
    # simpler: Off set = lines NOT in the span of the other simple roots
    def inspan(l):
        try: solve(rows,l); return True
        except AssertionError: return False
    T=[t for t,l in enumerate(L) if not inspan(l)]
    out.write('%d %d %s\n'%(k,len(T),' '.join(map(str,T)))); print('drop simple',k,'|Off|',len(T))
# also E6-type: drop the two nodes giving |Off|=84
