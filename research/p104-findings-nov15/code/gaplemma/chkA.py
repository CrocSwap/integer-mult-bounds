import numpy as np, sys, glob
spec=sys.argv[1]; sys.argv=['x',spec,'0','0']
exec(open('locgen.py').read().split('rng=')[0])
for f in sorted(glob.glob('loc_%s_*.npy'%spec)):
    z=np.load(f); X,Y,W,Zm,B=unpack(z); G=Y.T@X
    print(f,'max|res| %.1e'%np.abs(res(z)).max(),'t',[round(G[2*s,2*s+1]*G[2*s+1,2*s],3) for s in range(K)])
    print('  X rows Delta\n',np.round(X[Dl],4),'\n  Y rows Delta\n',np.round(Y[Dl],4))
    print('  smin X',np.linalg.svd(X,compute_uv=False)[-1], 'B vec', np.round(X@B,4).T)
