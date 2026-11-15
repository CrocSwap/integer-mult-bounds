"""[C] check proof ingredients on the nested B L=4 solution (NONNEST sol_ctlB4_2.npy, t=-0.5): K=I+L-U-diag rank 2, Q_a eigenvalues 1+-sqrt(t/(1+t)) (never 2),
Floor independence of X_0..X_k, X_r|H for k=0 (left arm 0..1, r = right stage)."""
import sys; sys.path.insert(0,'.'); import numpy as np
from rs2 import Model, two_arm
n,o,th=two_arm(4,2); m=Model(n,o,-0.5,()); z=np.load('sol_ctlB4_2.npy'); X,Y=m.unpack(z)
print('residual',np.max(np.abs(m.fj(z)[0])))
G=Y@X.T; N=m.N; K=np.eye(N)+np.tril(G,-1)-np.triu(G,1)-np.diag(np.diag(G))
U,s,Vt=np.linalg.svd(K); print('rank K sv', np.round(s[:4],6)); W=U[:,:2]*s[:2]; Zm=Vt[:2].T
for st,(u0,mask) in enumerate(m.stages):
    i=[u0,u0+1]; Gs=G[np.ix_(i,i)]; Wa=W[i]; Za=Zm[i]; Q=np.eye(2)-np.linalg.inv(Wa)@Gs@np.linalg.inv(Za.T)
    t=Gs[0,1]*Gs[1,0]; print('stage',st,'t',round(t,6),'eig Q',np.round(np.linalg.eigvals(Q),6),'pred',np.round([1+np.sqrt(complex(t/(1+t))),1-np.sqrt(complex(t/(1+t)))],6))
# Floor k=0: columns X_0 (2), X_r|H (2) with rows Y_0,Y_1 ; H = hubs {0,1}
st=m.stages; r=st[-1][0]; H=[0,1]
cols=[X[st[0][0]],X[st[0][0]+1]]+[np.where(np.isin(np.arange(n),H),X[u],0) for u in (r,r+1)]
print('Floor k=0 rank', np.linalg.matrix_rank(np.array(cols),tol=1e-8),'of 4')
