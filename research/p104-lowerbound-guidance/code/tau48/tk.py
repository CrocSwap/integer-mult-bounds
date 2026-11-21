"""TAU48 tk.py: per-row tau-forms T_k(x,y)=sum(Q[x o a_k, y o b_k])/2 mod 2 on Xs x Ys; check bilinear sum = X|, ranks."""
import sys,numpy as np; sys.path.insert(0,'../orbitlp'); sys.path.insert(0,'../double56')
from geo import Q
from rho import *
from e8xy_lib import xy_spaces
n=104
def rk(M): return f2rank([toint(r) for r in M%2]) if len(M) else 0
def analyse(W,V,name):
    W=W%4;V=V%4;a=W%2;b=V%2;N=(a@b.T)*Q;assert not (N%2).any();X=(N//2)%2
    RB=spaces_B(W,V,Q);RA=spaces_A(W,V,Q)
    Xs,Ys,vb,va=xy_spaces(RB,RA,n)
    if len(Xs)==0 or len(Ys)==0:
        print(name,'rhoB<=',vb,'rhoA<=',va,'dims',len(Xs),len(Ys),'rank X| 0 (empty)','cost',cost(W,V,Q)); return Xs,Ys
    tot=np.zeros((len(Xs),len(Ys)),int); rks=[]
    for k in range(W.shape[1]):
        Bk=(Q*a[:,k][:,None]*b[:,k][None,:])  # (a_k b_k^T) o Q
        S=Xs@Bk@Ys.T; assert not (S%2).any()
        Tk=(S//2)%2; tot=(tot+Tk)%2; rks.append(rk(Tk))
    assert ((tot-(Xs@X@Ys.T))%2==0).all()
    print(name,'rhoB<=',vb,'rhoA<=',va,'dims',len(Xs),len(Ys),'rank X|',rk(tot),'rank T_k',rks,'sum',sum(rks),'cost',cost(W,V,Q))
    return Xs,Ys
if __name__=='__main__':
    W8=np.load('../orbitlp/e8W.npy');V8=np.load('../orbitlp/e8V.npy')
    analyse(W8,V8,'E8')
