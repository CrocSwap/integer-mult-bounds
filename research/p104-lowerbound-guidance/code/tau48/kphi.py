"""TAU48 kphi.py: fixed-point space K = {x in Xs : x^T(I+X) = 0 on J'} ; bound rho_A+rho_B >= 2n-|J'|-dim K (and swapped)."""
import sys,json,numpy as np; sys.path.insert(0,'../orbitlp'); sys.path.insert(0,'../double56')
from geo import Q, D56
from rho import *
from e8xy_lib import xy_spaces, nullsp
n=104
def rk(M): return f2rank([toint(r) for r in M%2]) if len(M) else 0
def kbound(W,V,name):
    W=W%4;V=V%4;a=W%2;b=V%2;N=(a@b.T)*Q;X=(N//2)%2;I=np.eye(n,dtype=int)
    RB=spaces_B(W,V,Q);RA=spaces_A(W,V,Q); rb=trank(RB,n,2); ra=trank(RA,n,2)
    vb,J=rado_ub(RB,n); va,Jp=rado_ub(RA,n)
    Xs,Ys,_,_=xy_spaces(RB,RA,n)
    IX=(I+X)%2; Jp_l=sorted(Jp); J_l=sorted(J)
    def kdim(S,M,cols):
        if len(S)==0: return 0
        return len(S)-rk((S@M)[:,cols])
    kA=kdim(Xs,IX,Jp_l); kB=kdim(Ys,IX.T,J_l)
    lem=n-rk(Xs@IX@Ys.T*0+Xs@Ys.T) if len(Xs) and len(Ys) else n
    print(name,'rho',ra+rb,'(Rado ub',va+vb,') |J|',len(J),'|Jp|',len(Jp),'dimXs',len(Xs),'dimYs',len(Ys),
          'dimK',kA,'bound',2*n-len(Jp)-kA,'dimK*',kB,'bound*',2*n-len(J)-kB,'lemma',lem,'rk(I+X)',rk(IX),flush=True)
if __name__=='__main__':
    E=json.load(open(D56+'e8base.json')); Cc=np.array(E['C'])[:104]; Gb=np.array(E['Gb'])
    from lin import inv4; from sa import complete
    W8=np.load('../orbitlp/e8W.npy');V8=np.load('../orbitlp/e8V.npy'); kbound(W8,V8,'E8-56')
    W0=Cc%4; V0=(Cc@Gb)%4; kbound(W0,V0,'E8 (C, C Gb)')
    rng=np.random.default_rng(1)
    for t in range(2):
        m=8+int(rng.integers(0,5))
        while True:
            Xm=rng.integers(0,4,(8,m)); Pi=inv4(Xm[:,:8])
            if Pi is not None: break
        Ym=np.zeros((8,m),dtype=np.int64); Ym[:,:8]=Pi.T; kbound((W0@Xm)%4,(V0@Ym)%4,'randfact')
    X8=np.load('../double56/e8X.npy'); Y8=np.load('../double56/e8Y.npy')
    for (i,j,c) in [(0,1,1),(2,5,2)]:
        X2=X8.copy(); Y2=Y8.copy(); X2[:,j]=(X2[:,j]+c*X2[:,i])%4; Y2[:,i]=(Y2[:,i]-c*Y2[:,j])%4
        kbound((Cc@X2)%4,(Cc@Y2)%4,'transv')
    for k in (5,7):
        W,V=complete(W8[:,:k],V8[:,:k],Q); kbound(W,V,'E8[:%d]+cmp'%k)
