# builders: E8 rational decoder data (W,U,v_h) and network families on Q96 / P104
from netlib import *
import pickle, os, random
from fractions import Fraction as Fr
def kernel_data():
    fn='kd.pkl'
    if os.path.exists(fn): return pickle.load(open(fn,'rb'))
    A=np.array(list(itertools.product(range(-2,3),repeat=8)))
    A=A[(A!=0).any(1)]; first=(A!=0).argmax(1); A=A[A[np.arange(len(A)),first]>0]
    V=Ah@A.T   # 104 x N
    cand=[]
    for i in range(A.shape[0]):
        D=np.nonzero(V[:,i])[0]
        if len(D)<8: continue
        bs=span([L[t] for t in D])
        if len(bs)==8:
            v=[x for x in range(1,512) if all(dot(x,y)==0 for y in bs)][0]; cand.append((tuple(A[i]),v))
    chosen=[]
    for a,v in cand:
        T=np.array([c[0] for c in chosen]+[a])
        if np.linalg.matrix_rank(T)==len(T): chosen.append((a,v))
        if len(chosen)==8: break
    pickle.dump(chosen,open(fn,'wb')); return chosen
def WU(n,chosen=None):
    chosen=chosen or kernel_data()
    A=np.array([c[0] for c in chosen]).T; Ainv=np.linalg.inv(A)
    W=Ah[:n]@A                                  # n x 8 integers
    U=[[None]*8 for _ in range(n)]
    det=round(abs(np.linalg.det(A))); Ai=np.rint(Ainv*det).astype(int)   # = det*Ainv up to sign
    sgn=1 if abs(np.linalg.det(A)-det)<1e-6 or True else 1
    # U = Ah A^{-T} / 4
    Uf=(Ah[:n]@Ainv.T)/4
    Ui=np.empty((n,8),dtype=object)
    inv4=pow(4,P-2,P)
    Adet=int(round(np.linalg.det(A)))
    Aadj=np.rint(Ainv*Adet).astype(int)          # exact adjugate (Ainv*det)
    invd=pow(Adet%P,P-2,P)
    for t in range(n):
        for h in range(8):
            Ui[t,h]=(int(sum(int(Ah[t,k])*int(Aadj[h,k]) for k in range(8)))*invd*inv4)%P
    return W,Ui,[c[1] for c in chosen]
def labspan(ports): return span([L[t] for t in ports])
def lr_net(n):
    W,U,vs=WU(n); N=Net(n)
    g=[N.add([L[t]],[],{t:1},{}) for t in range(n)]
    for h in range(8):
        N.add([vs[h],1],[vs[h]],{}, {s:int(W[s,h])%P for s in range(n) if W[s,h]}, {g[t]:int(U[t,h]) for t in range(n) if U[t,h]%P})
    return N
def e8_net(n,kdims=None,withv=None,seed=0):
    """each hub row split: gather node (full F_h, chart a=span labels supp U[:,h]) -> deposit node (chart c, dim k) .
    kdims[h]=None: single node. else c=random k-dim subspace of a (containing v_h if withv)."""
    W,U,vs=WU(n); N=Net(n); rng=random.Random(seed)
    for h in range(8):
        Fh={t:int(U[t,h]) for t in range(n) if U[t,h]%P}; Gh={s:int(W[s,h])%P for s in range(n) if W[s,h]}
        a=labspan(Fh); v=vs[h]
        bfull=[v] if inspan(a,v) else []
        k=None if kdims is None else kdims[h]
        if k is None:
            N.add(a,bfull,Fh,Gh)
        else:
            # chart c of dim k inside a, containing v if possible and requested
            basis=list(a); rng.shuffle(basis)
            c=[v] if (inspan(a,v) and (withv is None or withv)) else []
            for x in basis:
                if len(span(c))>=k: break
                c=span(c+[x]) if True else c
            c=span(c)[:max(k,len(c))]
            g=N.add(a,c,Fh,{})
            bd=[x for x in c if all(dot(x,L[s])==0 for s in Gh)]   # c ∩ D^perp (basis-level: use v if in c)
            bd=[v] if inspan(c,v) else []
            N.add(c,bd,{},Gh,{g:1})
    return N
