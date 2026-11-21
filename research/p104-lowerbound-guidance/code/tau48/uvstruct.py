"""TAU48 struct.py: structure of U, V (J=all case) vs canonical codes."""
import sys,numpy as np
from gibbs import *
from canon import basis, R, perp
def sp(rows): return basis(rows) if len(rows) else np.zeros((0,n),int)
def dim(rows): return f2rank([toint(r) for r in rows%2]) if len(rows) else 0
def inter(A,B): return dim(A)+dim(B)-dim(np.concatenate([A,B]))
def anal(W,V,tag):
    W=W%4;V=V%4
    RB=spaces_B(W,V,Q);RA=spaces_A(W,V,Q)
    bits=lambda x: np.array([(x>>(n-1-s))&1 for s in range(n)])
    Vs=sp([bits(x) for t in range(n) for x in RB[t]]); Us=sp([bits(x) for t in range(n) for x in RA[t]])
    C1=basis(R[1]);C2=basis(R[2]);C3=basis(R[3])
    print(tag,'dimU',dim(Us),'dimV',dim(Vs),'U^V',inter(Us,Vs),'rank<U,V>',rk(Us@Vs.T),'rank<U,U>',rk(Us@Us.T),
      'U^C',inter(Us,C1),'V^C',inter(Vs,C1),'U^R2',inter(Us,C2),'V^R2',inter(Vs,C2),'U^R3',inter(Us,C3),'V^R3',inter(Vs,C3),
      'tau(J=all)',n-dim(Us)-dim(Vs)+rk(Us@Vs.T))
if __name__=='__main__':
    anal(np.load('../orbitlp/e8W.npy'),np.load('../orbitlp/e8V.npy'),'E8')
    for f in sys.argv[1:]: anal(np.load('g_W_%s.npy'%f),np.load('g_V_%s.npy'%f),f)
