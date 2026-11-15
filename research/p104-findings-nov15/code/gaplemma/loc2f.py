"""GAPLEMMA loc2f.py [N]: loc2 + F1 enforced (Cx [X_<=2, e_H] = I_8, Cy [Y_<=2, e_H] = I_8) + t_s != -1 (u_s(1+t_s)=1)."""
import numpy as np, sys
exec(open('loc2.py').read().split('def diag')[0].replace('dim=nxy+24+12+1','dim=nxy+24+12+1+144+3'))
H=np.zeros((n,2));H[0,0]=H[1,1]=1
base=nxy+37
def res2(z):
    r=list(res(z)); X,Y,W,Zm,b1,b2,u=unpack(z); G=Y.T@X
    Cx=z[base:base+72].reshape(8,9); Cy=z[base+72:base+144].reshape(8,9); us=z[base+144:base+147]
    r+=list((Cx@np.hstack([X,H])-np.eye(8)).ravel()); r+=list((Cy@np.hstack([Y,H])-np.eye(8)).ravel())
    for s in range(3): r.append(us[s]*(1+G[2*s,2*s+1]*G[2*s+1,2*s])-1)
    return np.array(r)
rng=np.random.default_rng(int(sys.argv[1])); ok=0; best=[]
for trial in range(int(sys.argv[2])):
    z0=rng.normal(size=dim)
    sol=least_squares(res2,z0,method='trf',max_nfev=4000,xtol=1e-15,ftol=1e-15,gtol=1e-15)
    m=np.abs(res2(sol.x)).max(); best.append(m)
    print(trial,'%.2e'%m,flush=True)
    if m<1e-9: ok+=1; np.save('loc2f_sol%d.npy'%trial,sol.x)
print('solved',ok,'best',min(best))
