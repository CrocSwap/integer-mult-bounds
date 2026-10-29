# all 6-dim subspaces of F2^9 (kernels of 3-dim dual subspaces, RREF enumeration) -> P112 line masks (lo,hi uint64)
import numpy as np, itertools
import p112 as p
PL=p.PL  # 112 labels
par=np.array([bin(x).count('1')&1 for x in range(512)])
mv=np.zeros((512,2),dtype=np.uint64)
for v in range(1,512):
    z=[i for i in range(112) if par[PL[i]&v]==0]
    lo=sum(1<<i for i in z if i<64); hi=sum(1<<(i-64) for i in z if i>=64)
    mv[v]=(lo,hi)
out=[]
n=9;m=3
for piv in itertools.combinations(range(n),m):
    free=[(i,c) for i in range(m) for c in range(n) if c not in piv and c>piv[i]]
    for b in itertools.product((0,1),repeat=len(free)):
        rows=[1<<q for q in piv]
        for (i,c),x in zip(free,b):
            if x: rows[i]|=1<<c
        out.append(rows)
R=np.array(out); print('3-dim dual subspaces:',len(R))
M=mv[R[:,0]]&mv[R[:,1]]&mv[R[:,2]]
pc=np.array([bin(int(a)).count('1')+bin(int(b)).count('1') for a,b in M[:2000]])
M.tofile('flats6.bin'); np.array(PL,dtype=np.int32).tofile('labels112.bin')
print('saved; sample max popcount',pc.max())
