"""GAPLEMMA chk2.py: F1 hub checks + structure on loc2 solutions."""
import numpy as np, glob, sys
sys.argv=['x']; 
exec(open('loc2.py').read().split('rng=')[0])
for f in sorted(glob.glob('loc2_sol*.npy')):
    z=np.load(f); X,Y,W,Zm,b1,b2,u=unpack(z); G=Y.T@X
    t=[G[2*s,2*s+1]*G[2*s+1,2*s] for s in range(3)]
    H=np.zeros((n,2));H[0,0]=H[1,1]=1
    f1=[np.linalg.svd(np.hstack([X[:,:2*j+2],H]),compute_uv=False)[-1] for j in range(3)]
    f1y=[np.linalg.svd(np.hstack([Y[:,:2*j+2],H]),compute_uv=False)[-1] for j in range(3)]
    rXD=np.linalg.matrix_rank(X[[4,5,6]],1e-7); rYD=np.linalg.matrix_rank(Y[[4,5,6]],1e-7)
    xs0=np.abs(X[4,:2]).max(); Ds=np.abs(X[[5,6]][:, :2]).max()
    print(f,'t',np.round(t,3),'F1x min sv',np.round(f1,3),'F1y',np.round(f1y,3),'rank X[Delta]',rXD,'Y[Delta]',rYD,'|x_0s| %.2f'%xs0)
