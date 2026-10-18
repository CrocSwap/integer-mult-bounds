# labels r mod 2E8 in simple-root coords; f(d)=max #labels in an affine (8-d)-flat of F2^8; Levi line counts
import numpy as np, itertools
from fractions import Fraction
from geom import L,G,n
# simple roots (doubled coords)
S=[[1,-1,-1,-1,-1,-1,-1,1],[2,2,0,0,0,0,0,0]]+[[0]*i+[-2,2]+[0]*(6-i) for i in range(7)]
S=[S[0],S[1]]+S[2:]
S=np.array(S[:8]); assert np.linalg.matrix_rank(S)==8
C=np.linalg.solve(S.T.astype(float),L.T.astype(float)).T
Ci=np.rint(C).astype(int); assert np.abs(C-Ci).max()<1e-9
lab=[int(''.join(str(x%2) for x in row),2) for row in Ci]
assert len(set(lab))==120 and 0 not in lab
labs=np.array(lab)
# enumerate subspaces of F2^8 of dim m (RREF, pivot=highest bit), max coset count
def subspaces(m):
    for piv in itertools.combinations(range(8),m):
        piv=sorted(piv,reverse=True)
        free=[[b for b in range(p) if b not in piv] for p in piv]
        for choice in itertools.product(*[range(1<<len(f)) for f in free]):
            basis=[]
            for p,f,ch in zip(piv,free,choice):
                v=1<<p
                for k,b in enumerate(f):
                    if ch>>k&1: v|=1<<b
                basis.append((p,v))
            yield basis
f={}
for d in range(1,9):
    m=8-d; best=0; cnt=0
    for basis in subspaces(m):
        cnt+=1; x=labs.copy()
        for p,v in basis: x=np.where((x>>p)&1==1,x^v,x)
        best=max(best,np.bincount(x).max())
    f[d]=int(best); print('d',d,'affine dim',m,'#subspaces',cnt,'max labels',best,flush=True)
print('f',f)
# Levi: lines orthogonal to fundamental coweights (dual basis of simple roots)
Sinv=np.linalg.inv(S.astype(float).T)  # columns? solve w_i.alpha_j=delta
W=np.linalg.inv(S.astype(float)).T  # rows w_i with S w_i^T = e_i
cnts=[int(sum(1 for r in L if abs(r@W[i])<1e-9)) for i in range(8)]
print('lines orthogonal to fundamental coweights',cnts)
assert f == {1: 64, 2: 36, 3: 20, 4: 12, 5: 8, 6: 4, 7: 2, 8: 1}, f
print('PASS Lemma S flats: f(d) = 64,36,20,12,8,4,2,1 over all 417199 subspaces of F2^8 (labels = root coordinates mod 2)')
