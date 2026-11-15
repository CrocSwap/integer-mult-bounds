import numpy as np, sys
sys.argv=['x']; exec(open('loc2.py').read().split('rng=')[0])
H=np.zeros((n,2));H[0,0]=H[1,1]=1
for f in ['loc2_sol5.npy','loc2_sol8.npy','loc2_sol21.npy','loc2_sol27.npy']:
    z=np.load(f); X,Y,W,Zm,b1,b2,u=unpack(z)
    for nm,M,ZZ in (('X',X,Zm),('Y',Y,W)):
        A=np.hstack([M,H]); U,S,Vt=np.linalg.svd(A); k=Vt[-1]; beta=k[:6]
        alpha=[np.linalg.solve(ZZ[2*s:2*s+2].T, beta[2*s:2*s+2]) if False else ZZ[2*s:2*s+2].T@beta[2*s:2*s+2] for s in range(3)]
        print(f,nm,'sv %.1e'%S[-1],'beta',np.round(beta,3),'Z^T beta (stage sums)',np.round(sum(alpha),4),'vec',np.round(M@beta,3))
